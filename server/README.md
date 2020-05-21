To run locally:

```
$ docker build -t ifserve .
$ run -p 5000:5000 ifserve
```

Then, do a POST to localhost:5000/

with a json payload in the body similar to:
  {
  	"token":"mytoken",
    "org_id":"myorgid",
    "label":"mylabel",
    "url":"urltomyinfluxdbinstance",
    "width":300,
    "height":300
  }