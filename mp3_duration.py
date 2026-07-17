import os
import sys
import unicodedata
from pathlib import Path
from mutagen.mp3 import MP3

def get_visual_width(s):
    """
    Calculate the visual width of a string, accounting for wide characters (e.g., Korean, Chinese).
    """
    width = 0
    for char in s:
        if unicodedata.east_asian_width(char) in ('W', 'F', 'A'):
            width += 2
        else:
            width += 1
    return width

def pad_string(s, width, align='left'):
    """
    Pads or truncates a string to fit a visual width, handling multi-byte characters correctly.
    """
    current_width = get_visual_width(s)
    if current_width > width:
        # Truncate and add ellipsis
        truncated = ""
        curr_w = 0
        for char in s:
            char_w = 2 if unicodedata.east_asian_width(char) in ('W', 'F', 'A') else 1
            if curr_w + char_w > width - 3:
                truncated += "..."
                break
            truncated += char
            curr_w += char_w
        s = truncated
        current_width = get_visual_width(s)
        
    padding = " " * (width - current_width)
    if align == 'left':
        return s + padding
    else:
        return padding + s

def format_duration(seconds):
    """
    Format seconds into HH:MM:SS or MM:SS depending on the length.
    """
    total_secs = int(seconds)
    hours = total_secs // 3600
    minutes = (total_secs % 3600) // 60
    secs = total_secs % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

def get_mp3_duration(file_path):
    """
    Extract the duration of an MP3 file using mutagen, convert to integer and add 1 second.
    """
    try:
        audio = MP3(file_path)
        # 초 단위로 1씩 플러스 처리 (정수형 초 + 1)
        return int(audio.info.length) + 1
    except Exception:
        return None

def main():
    # Check if directory path is passed as command line argument
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        # Prompt user to enter directory path
        try:
            folder_path = input("MP3 파일이 있는 폴더 경로를 입력하세요: ").strip()
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다.")
            sys.exit(0)
    
    # Remove quotes (common when dragging & dropping a folder to the terminal)
    if (folder_path.startswith('"') and folder_path.endswith('"')) or \
       (folder_path.startswith("'") and folder_path.endswith("'")):
        folder_path = folder_path[1:-1]
        
    path = Path(folder_path)
    
    if not path.exists():
        print(f"오류: 입력하신 경로가 존재하지 않습니다: {folder_path}", file=sys.stderr)
        return
        
    if not path.is_dir():
        print(f"오류: 입력하신 경로는 폴더가 아닙니다: {folder_path}", file=sys.stderr)
        return
        
    # Find all MP3 files (case-insensitive)
    mp3_files = [p for p in path.iterdir() if p.is_file() and p.suffix.lower() == '.mp3']
    
    if not mp3_files:
        print(f"폴더 내에 MP3 파일이 없습니다: {path.resolve()}")
        return
        
    print(f"\n[ 폴더 경로: {path.resolve()} ]")
    print("=" * 80)
    # File name column width 58, Duration column width 18
    print(f"{pad_string('파일명', 58)} | {pad_string('길이 (시간:분:초)', 18, 'right')}")
    print("-" * 80)
    
    total_seconds = 0.0
    valid_count = 0
    
    for file in sorted(mp3_files, key=lambda x: x.name):
        duration = get_mp3_duration(file)
        if duration is not None:
            formatted = format_duration(duration)
            total_seconds += duration
            valid_count += 1
            print(f"{pad_string(file.name, 58)} | {pad_string(formatted, 18, 'right')}")
        else:
            print(f"{pad_string(file.name, 58)} | {pad_string('재생 시간 분석 실패', 18, 'right')}")
            
    print("=" * 80)
    print(f"총 MP3 파일 개수: {len(mp3_files)}개 (분석 성공: {valid_count}개)")
    print(f"총 재생 시간: {format_duration(total_seconds)}")
    print("=" * 80)

if __name__ == "__main__":
    main()
