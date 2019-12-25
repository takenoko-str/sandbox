```
$ aws s3api get-object --bucket <s3_bucket_name> --key <s3_key> <outfile>
$ ls <outfile>
<outfile>
$ aws s3api get-object-tagging --bucket <s3_bucket_name> --key <s3_key>
{
    "TagSet": []
}
```
[公式ドキュメント](https://docs.aws.amazon.com/cli/latest/reference/s3api/get-object-tagging.html)
[Qiitaブログ](https://qiita.com/hitomatagi/items/69ac6d1037b926047010)
