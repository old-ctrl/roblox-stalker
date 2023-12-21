import requests
import time

USERNAME = ''
webhook_url = ""
security_token = ""

session = requests.Session()
session.headers.update({'Content-Type': 'application/json'})
session.cookies[".ROBLOSECURITY"] = security_token

def fetch_user_id_by_username(username):
    try:
        response = session.post('https://users.roblox.com/v1/usernames/users', json={"usernames": [username], "excludeBannedUsers": True})
        data = response.json().get('data', [])
        return data[0].get("id") if data else None
    except requests.RequestException as e:
        print(f"Error fetching user ID: {e}")
        return None
    
def fetch_latest_badge(user_id):
    response = session.get(f'https://badges.roblox.com/v1/users/{user_id}/badges?limit=10&sortOrder=Desc')
    if response.status_code == 200:
        badges = response.json().get('data', [])
        return badges[0] if badges else None
    else:
        print(f"Failed to fetch badges for user {user_id}")
        return None

def fetch_user_data(user_id):
    endpoints = {
        "user_info": f'https://users.roblox.com/v1/users/{user_id}',
        "friends": f"https://friends.roblox.com/v1/users/{user_id}/friends",
        "groups": f"https://groups.roblox.com/v2/users/{user_id}/groups/roles",
        "followers": f"https://friends.roblox.com/v1/users/{user_id}/followers",
        "following": f"https://friends.roblox.com/v1/users/{user_id}/followings",
        "badges": f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=10&sortOrder=Desc",
        "presence": "https://presence.roblox.com/v1/presence/users"
    }
    user_info = session.get(endpoints['user_info']).json()
    friends = {f.get("name") for f in session.get(endpoints['friends']).json().get("data", [])}
    groups = {g.get("group").get("name") for g in session.get(endpoints['groups']).json().get("data", [])}
    followers = {f.get("name") for f in session.get(endpoints['followers']).json().get("data", [])}
    following = {f.get("name") for f in session.get(endpoints['following']).json().get("data", [])}
    presence = session.post(endpoints['presence'], json={"userids": [user_id]}).json().get("userPresences", [])[0]

    #fetch latest badge
    latest_badge = fetch_latest_badge(user_id)

    return user_info, friends, groups, followers, following, presence, latest_badge

def fetch_avatar_url(user_id):
    params = {"userIds": user_id, "size": "720x720", "format": "Png", "isCircular": False}
    return session.get("https://thumbnails.roblox.com/v1/users/avatar", params=params).json().get("data", [])[0].get("imageUrl")

def post_to_webhook(username, text, avatar_url, user_id):
    payload = {
        "avatar_url": avatar_url,
        'content': '<@668158610504941579>',
        "embeds": [{"title": username, 'url': f'https://www.roblox.com/users/{user_id}/profile', "description": text, 'image': {'url': avatar_url}}]
    }
    session.post(webhook_url, json=payload)

def check_for_changes(current_data, previous_data, user_id, last_followed, last_unfollowed, last_badge):
    current_username, current_friends, current_groups, current_followers, current_following, current_presence, current_badge = current_data
    prev_username, prev_friends, prev_groups, prev_followers, prev_following, prev_presence, prev_badge = previous_data
    avatar_url = fetch_avatar_url(user_id)

    # Check for display name change
    if current_username['displayName'] != prev_username['displayName']:
        post_to_webhook(current_username['displayName'], f"{prev_username['displayName']} has changed their display name to {current_username['displayName']}", avatar_url, user_id)

    # Check for friends changes
    new_friends = current_friends - prev_friends
    lost_friends = prev_friends - current_friends
    for friend in new_friends:
        post_to_webhook(current_username['displayName'], f"{current_username['displayName']} has a new friend: `{friend}`", avatar_url, user_id)
    for friend in lost_friends:
        post_to_webhook(current_username['displayName'], f"{current_username['displayName']} lost a friend: `{friend}`", avatar_url, user_id)

    # Check for groups changes
    new_groups = current_groups - prev_groups
    lost_groups = prev_groups - current_groups
    for group in new_groups:
        post_to_webhook(current_username['displayName'], f"{current_username['displayName']} has joined a new group: `{group}`", avatar_url, user_id)
    for group in lost_groups:
        post_to_webhook(current_username['displayName'], f"{current_username['displayName']} has left the group: `{group}`", avatar_url, user_id)

    # Check for followers and following changes
    new_followers = current_followers - prev_followers
    lost_followers = prev_followers - current_followers
    for follower in new_followers:
        post_to_webhook(current_username['displayName'], f"{current_username['displayName']} has a new follower: `{follower}`", avatar_url, user_id)
    for follower in lost_followers:
        post_to_webhook(current_username['displayName'], f"{current_username['displayName']} lost a follower: `{follower}`", avatar_url, user_id)

    # Check for new and lost followings
    new_following = current_following - prev_following
    lost_following = prev_following - current_following

    # Check for new followings
    if new_following and last_followed not in new_following:
        new_followed_user = new_following.pop()
        last_followed = new_followed_user
        post_to_webhook(current_username['displayName'], f"{current_username['displayName']} is now following: `{new_followed_user}`", avatar_url, user_id)

    # Check for lost followings
    if lost_following and last_unfollowed not in lost_following:
        new_unfollowed_user = lost_following.pop()
        last_unfollowed = new_unfollowed_user
        post_to_webhook(current_username['displayName'], f"{current_username['displayName']} stopped following: `{new_unfollowed_user}`", avatar_url, user_id)

    # Check for new badge
    if current_badge and (not prev_badge or current_badge["id"] != prev_badge["id"]):
        badge_name = current_badge.get("name")
        post_to_webhook(current_username['displayName'], f"{current_username['displayName']} has been awarded the '{badge_name}' badge.", avatar_url, user_id)
        last_badge = current_badge["id"]

    # Check for presence changes
    if current_presence != prev_presence:
        presence_status = "Offline"
        if current_presence["userPresenceType"] == 1:
            presence_status = "Online on Website"
        elif current_presence["userPresenceType"] == 2:
            presence_status = f"Playing {current_presence['lastLocation']}"
        elif current_presence["userPresenceType"] == 3:
            presence_status = "Online on Mobile"
        post_to_webhook(current_username['displayName'], f"{current_username['displayName']} is now {presence_status}", avatar_url, user_id)

    return last_followed, last_unfollowed, last_badge


def main():
    user_id = fetch_user_id_by_username(USERNAME)
    if not user_id:
        print(f"User not found: {USERNAME}")
        return

    last_followed = None
    last_unfollowed = None
    last_badge = None

    try:
        previous_data = fetch_user_data(user_id)

        while True:
            time.sleep(5)
            current_data = fetch_user_data(user_id)

            last_followed, last_unfollowed, last_badge = check_for_changes(current_data, previous_data, user_id, last_followed, last_unfollowed, last_badge)

            previous_data = current_data

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

