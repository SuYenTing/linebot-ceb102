#!bin/bash
# 讀取ngrok的資訊(JSON檔案格式)
curl $(docker port chatbot_ngrok 4040)/api/tunnels > tunnels.json

# 利用jq(處理Json檔案格式工具)找出ngrok產生的public_url
docker run -v $(pwd)/tunnels.json:/tmp/tunnels.json --rm  realguess/jq jq .tunnels[1].public_url /tmp/tunnels.json 

# 刪除檔案
rm tunnels.json