"""
Check if MP3 file has embedded cover art
"""
from mutagen.mp3 import MP3
from mutagen.id3 import APIC

mp3_path = r"E:\CodeSpace\Auto-Suno-App\songs-download\Snowfall On The Vinyl__ID__ee0cced1-b3c2-43b3-b90a-a70183b5af54.mp3"

try:
    audio = MP3(mp3_path)
    
    if audio.tags:
        print("✅ File has ID3 tags")
        print(f"\n📋 Metadata:")
        print(f"   Title: {audio.tags.get('TIT2', 'N/A')}")
        print(f"   Artist: {audio.tags.get('TPE1', 'N/A')}")
        print(f"   Album: {audio.tags.get('TALB', 'N/A')}")
        print(f"   Genre: {audio.tags.get('TCON', 'N/A')}")
        
        # Check for cover art
        apic_frames = audio.tags.getall('APIC')
        if apic_frames:
            print(f"\n🖼️  Cover Art: ✅ Found {len(apic_frames)} image(s)")
            for idx, apic in enumerate(apic_frames, 1):
                print(f"   Image {idx}: {apic.mime} - {len(apic.data)} bytes")
        else:
            print("\n🖼️  Cover Art: ❌ NOT FOUND")
    else:
        print("❌ File has NO ID3 tags")
        
except Exception as e:
    print(f"❌ Error: {e}")
