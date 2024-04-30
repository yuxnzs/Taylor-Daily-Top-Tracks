import requests
from bs4 import BeautifulSoup
import pandas as pd

# 將過長的歌名縮短
def shorten_title(title):
    if len(title) >= 60:
        return title[:60] + "..."
    else:
        return title


# 網站 URL，可透過更改其 Spotify ID 來換歌手
url = "https://kworb.net/spotify/artist/06HL4z0CvFAxyc27GXpf02_songs.html"

# 向網站發送 GET 請求
response = requests.get(url)

# 檢查請求是否成功
if response.status_code == 200:
    # 解析 HTML 內容
    soup = BeautifulSoup(response.content, 'html.parser')

    # 找到含有歌曲數據的表格
    table = soup.find('table', class_='addpos')

    # 存取爬出來的數據
    song_titles, streams, daily_counts = [], [], []

    # 循環處理表格中的每一行（跳過標題行）
    for row in table.find_all('tr')[1:]:
        cells = row.find_all('td')
        # 歌曲標題、總播放量及每日播放量
        song_title = cells[0].get_text(strip=True)
        # 排序用，所以要轉成 int
        stream_count = int(cells[1].get_text(strip=True).replace(',', ''))
        daily_count = int(cells[2].get_text(strip=True).replace(',', ''))

        song_titles.append(song_title)
        streams.append("{:,}".format(stream_count))
        daily_counts.append("{:,}".format(daily_count))

    # 使用提取的數據創建 DataFrame
    df = pd.DataFrame({
        'Song Title': song_titles,
        'Streams': streams,
        'Daily': daily_counts
    })

    # 根據 Daily 每日播放量降序排序 DataFrame（這裡需要再次轉換為數字進行排序）
    df['Daily'] = df['Daily'].str.replace(',', '').astype(int)
    sorted_df = df.sort_values(by='Daily', ascending=False).reset_index(drop=True)

    # 調整索引從 1 開始
    sorted_df.index += 1

    # 再次將排序後的 Daily 每日播放量欄位格式化為每三位一撇
    sorted_df['Daily'] = sorted_df['Daily'].apply(lambda x: "{:,}".format(x))
    sorted_df['Song Title'] = sorted_df['Song Title'].apply(shorten_title)

    # print 出排序後的 DataFrame，並顯示索引編號
    print(sorted_df.to_string(index=True))
else:
    print(f"無法取得數據。狀態碼: {response.status_code}")
