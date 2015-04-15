## canvas-ping-pong-multiplayer ##

This is example of implementaion canvas ping pong game by [Mailson's tutorial][lnk1] with multiplayer extension.

<div style="text-align: center">
<img src="http://rikanishu.github.io/images/canv.png" />
</div>

### Installing ###

* Install server dependings
	* Python >= 2.7.2
	* Tornado >= 2.4
* Run server via command line

```
user@example:~$ sudo pip install tornado
user@example:~$ python ./app.py
```
* Open ```client/index.html``` in browser

### Configure ###

See ```server/config.py``` and variable gameOptions in client for details

### Notes ###

Is not completed yet, has todos and sync problems


[lnk1]: http://blog.mailson.org/2013/02/simple-pong-game-using-html5-and-canvas/
