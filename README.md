# Facebook crawler

1. Prerequisites

    - Download firefox portable at <https://portableapps.com/apps/internet/firefox_portable>
    - Download geckodriver at <https://github.com/mozilla/geckodriver/releases>
    - Install `selenium` with `pip install selenium`

2. Loop scrolling to load as much facebook urls as possible:

    - **Log in** to your facebook account
    - Find a page and go to its photo section
    - Run this code in console:

    ```javscript
    for (i=0; i<1000;i++) {await new Promise(r => setTimeout(r, 200));
    window.scrollTo(0, document.body.scrollHeight);}
    ```

3. Get facebook urls:

    - Run this code in console:

    ```javascript
    function getElementsByXPath(xpath)
    {
        let results = [];
        let query = document.evaluate(xpath, document,
            null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        for (let i = 0, length = query.snapshotLength; i < length; ++i) {
            results.push(query.snapshotItem(i));
        }
        return results;
    }

    str = ''
    s = new Set()
    getElementsByXPath("//a[contains(@href,'/photo.php')]/@href").forEach(item=>s.add(item.value))
    s.forEach(e=>str+=e+'\n')
    s = new Set()
    getElementsByXPath("//a[contains(@href,'/photos')]/@href").forEach(item=>s.add(item.value))
    s.forEach(e=>str+=e+'\n')
    var blob = new Blob([str], {type: 'text/plain'});
    var url = window.URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'links.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    ```

    - Copy the output to a txt file

4. Run the crawler:

    - Run `python crawler.py <txt file>`
    - The result will be saved in a `csv` file with the same name as the `txt` file.
    - ***Note***: You do not need to log in to your facebook account to run the crawler. Thus, it can be sped up using multiple browser instances.

5. `TSV` structure (v1):

    | url | img_url | date_str | year | month | day | hour | minute | filename | error |
    |:---:|:-------:|:--------:|------|:-----:|-----|------|--------|----------|-------|
    |     |         |          |      |       |     |      |        |          |       |

    - `url`: the url of the facebook post
    - `img_url`: the url of the image
    - `date_str`: the date string of the post
    - `year`: the year of the post
    - `month`: the month of the post
    - `day`: the day of the post
    - `hour`: the hour of the post
    - `minute`: the minute of the post
    - `filename`: the filename of the image
    - `error`: the error message if the image cannot be downloaded
