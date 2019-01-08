1. Save crendentials.json according to step one in this [doc](https://developers.google.com/drive/api/v3/quickstart/python)
2. Run `authenticate.py`
3. Run `share_dir.py -h` to see how to use it. Then run the script.

Example:
```
./share_dir.py -d 1234abcdasdfqwerasdf3456ASDFQWERi \
	--file-suffix .tar.gz \
	--email-suffix berkeley.edu \
	-E ./email_message.txt \
	--yes
```

