import datetime
from hero_kda_winrate import hero_kda_winrate
from bp import bp

class update():
    def check_version(self):
        with open('my_app_version.txt',encoding='utf8') as f:
            version = f.read()
        if version != datetime.datetime.now().strftime("%Y-%m-%d"):
            KDA = hero_kda_winrate()
            KDA.hero_kda_winrate_main()
            BP = bp()
            BP.bp_main()
            print('OK')
        else:
            print('版本相同')
            

    def update(self):
        with open('my_app_version.txt','w',encoding='utf8') as f:
            f.write(datetime.datetime.now().strftime("%Y-%m-%d"))

    def update_main(self):
        self.check_version()
        self.update()

if __name__=='__main__':
    UP = update()
    UP.update_main()