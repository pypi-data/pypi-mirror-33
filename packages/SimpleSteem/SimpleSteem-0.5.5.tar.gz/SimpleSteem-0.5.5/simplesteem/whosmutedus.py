    def get_whos_muted_us(self):
        following = self.util.who_im_following(self.cfg.mainaccount)
        time.sleep(3)
        for f in following:
            print ("Checking " + f)
            h = self.util.get_my_history(f)
            for a in h:
                if a[1]['op'][0] == "custom_json":
                    j = a[1]['op'][1]['json']
                    d = json.loads(j)
                    for i in d[1]:
                        if i == "what":
                            if len(d[1]['what']) > 0:
                                if d[1]['what'][0] == "ignore":
                                    if d[1]['follower'] == "artturtle":
                                        print ("this bitch muted us")
