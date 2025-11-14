import instaloader
import os
import sys
from pathlib import Path

def display_menu():
    """Display the main menu options"""
    print("\n" + "="*50)
    print("      INSTAGRAM DOWNLOADER - MAIN MENU")
    print("="*50)
    print("1. Download all posts from a profile")
    print("2. Download single post by URL/shortcode")
    print("3. Download profile picture only")
    print("4. Download stories (if available)")
    print("5. Download highlights (if available)")
    print("6. Set download options")
    print("7. Exit")
    print("="*50)

def get_user_choice():
    """Get user choice with validation"""
    try:
        choice = input("\nEnter your choice (1-7): ").strip()
        return int(choice)
    except ValueError:
        print("❌ Please enter a valid number!")
        return None

def setup_download_options():
    """Configure download options interactively"""
    print("\n📁 DOWNLOAD OPTIONS SETUP")
    print("-" * 30)
    
    options = {
        'download_videos': ask_yes_no("Download videos?"),
        'download_profile_pic': ask_yes_no("Download profile picture?"),
        'download_comments': ask_yes_no("Download comments?"),
        'save_metadata': ask_yes_no("Save metadata (JSON)?"),
        'compress_json': ask_yes_no("Compress JSON files?"),
        'filename_pattern': ask_filename_pattern(),
        'max_posts': ask_max_posts()
    }
    
    return options

def ask_yes_no(question):
    """Ask yes/no question and return boolean"""
    while True:
        response = input(f"{question} (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("❌ Please enter 'y' or 'n'")

def ask_filename_pattern():
    """Ask user for filename pattern"""
    print("\n📝 Filename patterns available:")
    print("   Default: {profile}_{date_utc}")
    print("   Options: {profile}, {date_utc}, {shortcode}, {mediaid}")
    pattern = input("Enter filename pattern (press Enter for default): ").strip()
    return pattern if pattern else "{profile}_{date_utc}"

def ask_max_posts():
    """Ask user for maximum number of posts to download"""
    while True:
        try:
            response = input("Max posts to download (0 for all, press Enter for all): ").strip()
            if not response:
                return None
            max_posts = int(response)
            return max_posts if max_posts > 0 else None
        except ValueError:
            print("❌ Please enter a valid number!")

def download_profile_posts():
    """Download all posts from a profile with interactive options"""
    username = input("\nEnter Instagram username (without @): ").strip()
    if not username:
        print("❌ Username cannot be empty!")
        return
    
    options = setup_download_options()
    
    print(f"\n🚀 Starting download for: @{username}")
    print("⏳ Please wait...")
    
    try:
        # Create instance with configured options
        L = instaloader.Instaloader(
            download_videos=options['download_videos'],
            download_geotags=False,
            download_comments=options['download_comments'],
            save_metadata=options['save_metadata'],
            compress_json=options['compress_json'],
            filename_pattern=options['filename_pattern']
        )
        
        # Get profile
        profile = instaloader.Profile.from_username(L.context, username)
        
        print(f"✅ Profile found: {profile.full_name}")
        print(f"📊 Total posts: {profile.mediacount}")
        print(f"📁 Downloading to: instagram_{username}")
        
        # Create download directory
        download_dir = Path(f"instagram_{username}")
        download_dir.mkdir(exist_ok=True)
        
        # Download posts with progress
        posts = profile.get_posts()
        if options['max_posts']:
            posts = list(posts)[:options['max_posts']]
            print(f"📥 Downloading {options['max_posts']} posts...")
        else:
            print(f"📥 Downloading all {profile.mediacount} posts...")
        
        downloaded_count = 0
        for post in posts:
            try:
                L.download_post(post, target=download_dir)
                downloaded_count += 1
                print(f"✅ Downloaded post {downloaded_count}: {post.date}")
            except Exception as e:
                print(f"❌ Error downloading post: {e}")
        
        # Download profile picture if requested
        if options['download_profile_pic']:
            try:
                L.download_profilepic(profile)
                print("✅ Profile picture downloaded")
            except Exception as e:
                print(f"❌ Error downloading profile picture: {e}")
                
        print(f"\n🎉 Download completed!")
        print(f"📂 Files saved in: {download_dir.absolute()}")
        print(f"📦 Total posts downloaded: {downloaded_count}")
        
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"❌ Profile '@{username}' does not exist!")
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        print(f"❌ Profile '@{username}' is private and you don't follow it!")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

def download_single_post():
    """Download a single post by URL or shortcode"""
    print("\n📸 SINGLE POST DOWNLOAD")
    print("-" * 30)
    
    url_input = input("Enter Instagram post URL or shortcode: ").strip()
    if not url_input:
        print("❌ URL/shortcode cannot be empty!")
        return
    
    # Extract shortcode from URL
    if "instagram.com" in url_input:
        shortcode = extract_shortcode_from_url(url_input)
        if not shortcode:
            print("❌ Invalid Instagram URL!")
            return
    else:
        shortcode = url_input
    
    options = setup_download_options()
    
    try:
        L = instaloader.Instaloader(
            download_videos=options['download_videos'],
            download_comments=options['download_comments'],
            save_metadata=options['save_metadata'],
            filename_pattern=options['filename_pattern']
        )
        
        print(f"⏳ Downloading post: {shortcode}")
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target="single_posts")
        
        print(f"✅ Post downloaded successfully!")
        print(f"📂 Saved in: single_posts/")
        
    except Exception as e:
        print(f"❌ Error downloading post: {e}")

def extract_shortcode_from_url(url):
    """Extract shortcode from Instagram URL"""
    import re
    pattern = r'instagram\.com/p/([^/?]+)'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def download_profile_pic_only():
    """Download only the profile picture"""
    username = input("\nEnter Instagram username: ").strip()
    if not username:
        print("❌ Username cannot be empty!")
        return
    
    try:
        L = instaloader.Instaloader()
        profile = instaloader.Profile.from_username(L.context, username)
        L.download_profilepic(profile)
        print(f"✅ Profile picture downloaded for @{username}")
    except Exception as e:
        print(f"❌ Error: {e}")

def download_stories():
    """Download stories if available"""
    username = input("\nEnter Instagram username: ").strip()
    if not username:
        print("❌ Username cannot be empty!")
        return
    
    try:
        L = instaloader.Instaloader()
        profile = instaloader.Profile.from_username(L.context, username)
        
        # Check if stories are available
        stories = L.get_stories([profile.userid])
        story_count = 0
        
        for user_story in stories:
            for story in user_story.get_items():
                L.download_storyitem(story, target=f"stories_{username}")
                story_count += 1
                print(f"✅ Downloaded story {story_count}")
        
        if story_count == 0:
            print("ℹ️  No stories available or profile is private")
        else:
            print(f"🎉 Downloaded {story_count} stories")
            
    except Exception as e:
        print(f"❌ Error downloading stories: {e}")

def download_highlights():
    """Download highlights if available"""
    username = input("\nEnter Instagram username: ").strip()
    if not username:
        print("❌ Username cannot be empty!")
        return
    
    try:
        L = instaloader.Instaloader()
        profile = instaloader.Profile.from_username(L.context, username)
        
        # Get highlights
        highlights = L.get_highlights(profile)
        highlight_count = 0
        
        for highlight in highlights:
            for item in highlight.get_items():
                L.download_storyitem(item, target=f"highlights_{username}")
                highlight_count += 1
                print(f"✅ Downloaded highlight {highlight_count}")
        
        if highlight_count == 0:
            print("ℹ️  No highlights available or profile is private")
        else:
            print(f"🎉 Downloaded {highlight_count} highlight items")
            
    except Exception as e:
        print(f"❌ Error downloading highlights: {e}")

def main():
    """Main function with interactive menu"""
    print("🔽 Instagram Media Downloader")
    print("   Download high-quality photos and videos")
    
    while True:
        display_menu()
        choice = get_user_choice()
        
        if choice == 1:
            download_profile_posts()
        elif choice == 2:
            download_single_post()
        elif choice == 3:
            download_profile_pic_only()
        elif choice == 4:
            download_stories()
        elif choice == 5:
            download_highlights()
        elif choice == 6:
            options = setup_download_options()
            print("✅ Options saved for next download!")
        elif choice == 7:
            print("\n👋 Thank you for using Instagram Downloader!")
            print("   Goodbye! 👋")
            break
        elif choice is None:
            continue
        else:
            print("❌ Invalid choice! Please select 1-7.")
        
        # Pause before showing menu again
        if choice != 7:
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Program interrupted by user!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)