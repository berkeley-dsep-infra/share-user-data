# share-user-data

This script facilitates the sharing of user data from a folder in Google Drive.
Suppose data has been uploaded to a Drive folder in the format of

 - user1.tar.gz
 - user2.tar.gz
 - user3.tar.gz
 - ...

This will share each file {username}.tar.gz with user1@{domain} and send an email
notification to them. It will also optionally unescape usernames that have 
previously been escaped (e.g. by JupyterHub).

## Instructions
1. Save crendentials.json according to step one of the [python quickstart](https://developers.google.com/drive/api/v3/quickstart/python) API guide.
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

By Simon Mo <xmo@berkeley.edu>
