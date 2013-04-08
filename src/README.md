## Notes

### Running on localhost

For the Flask development environment to work, you need to add `linkitup.dev` to your hosts file. The reason is that JavaScript security gets confused, as `localhost` and `127.0.0.1` are not always equivalent: you'll have a separate session cookie for each host. 

On Mac, in `/private/etc/hosts`, just add `linkitup.dev` to the line with localhost on it (you need to `sudo` to edit)

Next step (on mac, again) is to refresh your DNS cache. This you can do by running `sudo dscacheutil -flushcache`. 

Look up the details for your favourite operating system.



