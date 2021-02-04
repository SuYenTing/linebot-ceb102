# Github簡介

# Line聊天機器人-CEB102課程小幫手

## 簡介

這個是我自己獨立製作的小專案，主要是透過Docker部署一個Line機器人，這個Line機器人可以主動推播訊息提醒學生上課時間，使用者也可以與機器人進行互動，輸入關鍵字查詢教學相關表單。詳細說明可參考我的[部落格文章](https://suyenting.github.io/post/linebot-ceb102-class-helper/)

## Line機器人架構圖

![](https://github.com/SuYenTing/linebot-ceb102/blob/main/LineBot-Framework.png)

## 檔案說明

* app：
    * curriculumToSQL.py： 將原始課表檔案做資料清洗並彙整至MySQL資料庫
    * keywordToSQL.py： 將linebot_keyword.json檔案資訊彙整至MySQL資料庫
    * linebot_keyword.json： Line機器人關鍵字對應訊息的Json檔案，因表單連結屬於私人資訊，故僅留範例連結
    * main.py： Flask主程式，Line機器人邏輯處理程式碼
    * secretFile.json： 存放帳密相關私人資訊，此處資料刪除，僅留格式下來提供參考
* dockerfile：
    * dockerfile-flask： 部署Python Flask會用到的部署檔案
* docker-compose.yml： Docker Compose部署程式碼
* get_ngrok_url.sh： 執行檔，在Docker部署完後執行，可取得Ngrok容器內產生的公開連結

## 執行說明

因有私人資訊，故依此Github內的檔案會無法順利執行程式。

此處列出我部署的步驟提供參考：

在資料夾路徑底下，輸入docker-compose指令：

```bash=
docker-compose up -d
```

部署好後，Flask會直接跑./app/main.py程式，接下來執行get_ngrok_url.sh取得Ngrok容器內的公開連結：

```bash=
bash get_ngrok_url.sh
```

shell畫面會印出公開連結網址，接下來將此公開連結網址放到Line Developer的Webhook連結，即可啟用Line機器人服務。
