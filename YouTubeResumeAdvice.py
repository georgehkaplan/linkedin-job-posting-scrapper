import os
import csv
from googleapiclient.discovery import build
import datetime as dt

# Set up YouTube API credentials
#api_key = "AIzaSyCgJDEfNimZ6pTU6VlRO1ZJjVdpD0ARBPI"

api_key = "AIzaSyCT-kg19n5KUSX07OZYM5mdFfgU19QHFIM"

# Set up YouTube API client
youtube = build('youtube', 'v3', developerKey=api_key)

def fetch_video_statistics(video_id):
    statistics_response = youtube.videos().list(
        part="statistics",
        id=video_id
    ).execute()

    if "items" in statistics_response:
        statistics_data = statistics_response["items"][0]["statistics"]
        like_count = statistics_data.get("likeCount", 0)
        dislike_count = statistics_data.get("dislikeCount", 0)
        view_count = statistics_data.get("viewCount", 0)
        return like_count, dislike_count, view_count
    else:
        return 0, 0, 0

# Search for United States videos with pagination
def search_youtube_videos(query, max_results):
    video_data = []

    next_page_token = None
    while True:
        # Define search parameters, including the query, publishedBefore date, and regionCode
        search_params = {
            'q': query,
            'publishedBefore': '2023-01-01T00:00:00Z',  # Videos published before 2023
            'maxResults': max_results,  # Number of results per page
            'type': 'video',
            'part': 'snippet',
            'regionCode': 'US',  # Restrict to United States
        }

        if next_page_token:
            search_params['pageToken'] = next_page_token

        search_response = youtube.search().list(**search_params).execute()

        # Process search results
        for search_result in search_response.get("items", []):
            video_id = search_result["id"]["videoId"]
            video_title = search_result["snippet"]["title"]
            video_published_at = search_result["snippet"]["publishedAt"]
            video_published_at = dt.datetime.strptime(video_published_at, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')

            # Fetch video statistics
            like_count, dislike_count, view_count = fetch_video_statistics(video_id)

            # Format the title and published date
            formatted_title = video_title.encode('utf-8').decode('unicode_escape')
            formatted_published_at = video_published_at

            video_data.append([video_id, formatted_title, formatted_published_at, like_count, dislike_count, view_count])

        next_page_token = search_response.get("nextPageToken")

        if not next_page_token:
            break

    return video_data

def write_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write header
        csv_writer.writerow(["Video ID", "Title", "Published At", "Like Count", "Dislike Count", "View Count"])
        # Write video data
        csv_writer.writerows(data)

if __name__ == "__main__":
    query = "How to land a job in 2023"  # Updated query
    max_results = 100  # Set the desired maximum number of results
    data = search_youtube_videos(query, max_results)
    if data:
        filename = f"{query}_videos.csv"
        write_to_csv(data, filename)
        print(f"Data exported to {filename}")
    else:
        print("No videos found for the given query.")