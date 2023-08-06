![Logo](https://raw.githubusercontent.com/sawyersteven/randomindexlist/master/img/Logo_wide.png)

# RandomIndexList
Ever wonder why lists start at `0`? Become the master of your own list objects and wonder no more! With RandomIndexList you'll create arrays that start at whichever number you please, or let RandomIndexList's state-of-the-art randomizer select a completely arbitrary starting index for you!

### Installation
RandomIndexList has been tested on Python 3.4.0 and 2.7.14. Others versions are likely to work just as well, but it would be best to just completely avoid this package if you value your sanity.

Install via pip with `pip install RandomIndexList`


### Usage
RandomIndexList extends Python's built-in List class and can be used in the same manner.

If you like to live on the edge you can let RandomIndexList pick a starting index for you.
	
    from RandomIndexList import RandomIndexList
    my_list = RandomIndexList(range(0, 5))
    my_list.index
    >>> 55
    my_list[56]
    >>> 1
    
If you have enough chaos in your life you can choose your own starting index.

    my_list = RandomIndexList(range(0, 5), index=95)
    my_list[97]
    >>> 2