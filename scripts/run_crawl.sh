
# not yets
ABSPATH =/d/Desktop/ych/side_project/geturl/linebot/botcode
echo "Start running crawler"
python "${ABSPATH}/script/runner_crawl.py"  > output.log 2>&1 &
echo "Finish running crawler"
