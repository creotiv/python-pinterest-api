# Pinterest API for Python [DEPRECATED]
This API was developed before Pinterest opened their official API, now it's not suppported. Please use official API https://developers.pinterest.com/ or fork this one and fix.

Example of use:
```
    p = Pinterest()
    logged = p.login('someeamil@gmail.com','password')
    if logged:
        print 'logged in.'
        boards = p.getBoards()
        print boards
        res = p.createPin(board=boards['art'],title='Anton Semenov | 30 Art Works',
            desc='Anton Semenov | 30 Art Works',
            media='http://1.bp.blogspot.com/-SfG0Ad5_UVo/UGxBfrBGugI/AAAAAAAAA54/o-glBuiX_3Q/s640/Black_dream_by_Gloom82.jpg',
            posturl='http://30artworks.blogspot.com/2012/10/anton-semenov.html')
        print 'pin created: %s' % res
```
