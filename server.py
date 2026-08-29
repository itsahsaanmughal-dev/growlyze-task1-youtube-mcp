import os
from fastmcp import FastMCP
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

mcp = FastMCP("YouTube-Remote-MCP")
API_KEY = os.environ.get("YOUTUBE_API_KEY", "")


def get_youtube_client():
  if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY is not set.")
  return build("youtube", "v3", developerKey=API_KEY)


@mcp.tool()
def search_youtube_videos(query: str, max_results: int = 5) -> str:
  """Search YouTube videos by keyword and return title, videoId, and description."""
  youtube = get_youtube_client()
  request = youtube.search().list(
      q=query, part="snippet", type="video", maxResults=max_results
  )
  response = request.execute()
  items = response.get("items", [])
  results = []
  for item in items:
    title = item["snippet"]["title"]
    vid = item["id"]["videoId"]
    channel = item["snippet"]["channelTitle"]
    results.append(f"- **{title}** (Channel: {channel}) | Video ID: `{vid}`")
  return "\n".join(results) if results else "No videos found."


@mcp.tool()
def get_video_transcript(video_id: str) -> str:
  """Fetch video transcript/captions text by videoId."""
  try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    text = " ".join([t["text"] for t in transcript])
    return text[:4000]
  except Exception as e:
    return f"Could not fetch transcript: {str(e)}"


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8080))
    # transport ko "http" ya "streamable-http" karein
    mcp.run(transport="http", host="0.0.0.0", port=port)