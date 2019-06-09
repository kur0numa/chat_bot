import sys  
import irc.bot  
import requests  

request_number = 0
now_song = 0
song_name = []
userlist = []
  
class TwitchBot(irc.bot.SingleServerIRCBot):  
    def __init__(self, username, client_id, token, channel):  
        self.client_id = client_id  
        self.token = token  
        self.channel = '#' + channel  
  
        # 채널 ID를 얻기 위해 new Twitch API 호출
        url = 'https://api.twitch.tv/helix/users?login=' + channel  
        headers = {'Client-ID': client_id}  
        r = requests.get(url, headers=headers).json()  
        self.channel_id = r['data'][0]['id']  
  
        # IRC bot 연결 생성  
        server = 'irc.chat.twitch.tv'  
        port = 6667  
        print('서버 ' + server + ', 포트 ' + str(port) + '에 연결 중...')  
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:' + token)], username, username)  
  
    def on_welcome(self, c, e):
        print(self.channel + '에 연결되었습니다.')  
  
        # 봇을 사용하기 전에 채널 권한 부여가 필요  
        c.cap('REQ', ':twitch.tv/membership')  
        c.cap('REQ', ':twitch.tv/tags')  
        c.cap('REQ', ':twitch.tv/commands')  
        c.join(self.channel)  
  
    def on_pubmsg(self, c, e):  

        print(e.tags)

        broadcaster = e.tags[1].get('value')
        moderater = e.tags[7].get('value')

        displayname = e.tags[3].get('value') # 누가 입력했는지 저장

        print(displayname) # 제대로 저장되었는지 출력해봄
        print(moderater)

        if e.arguments[0][:1] == '+':  
            cmd = e.arguments[0].split(' ')[0][1:] 
            print('Received command: ' + cmd)


            if broadcaster == 'broadcaster/1' or moderater == '1':
                
                if cmd == '초기화' or cmd == '다음곡':
                    self.do_op_command(e, cmd)
                else:
                    self.do_command(e, cmd)
                    

            else:
                self.do_command(e, cmd)  


    def do_op_command(self, e, cmd):
        c = self.connection

        global request_number
        global now_song
        global song_name
        global userlist

        # 나만 사용가능한 명령어
        if cmd == '초기화':
            request_number = 0
            now_song = 0
            song_name = []
            userlist = []
            
            message = "초기화가 완료되었습니다!"
            c.privmsg(self.channel, message)

        elif cmd == '다음곡':
            if now_song < request_number:
                print(song_name[now_song]) # 테스트용
                print(request_number, now_song)
                c.privmsg(self.channel, "다음 신청곡은 " + str(song_name[now_song]) + ", 신청자는 >> " + str(userlist[now_song]) + " << 입니다 :)")
                request_number -= 1
                print(now_song)
                userlist.pop(0)
                song_name.pop(0)

            else:
                c.privmsg(self.channel, "더이상 신청곡이 없습니다!")

  
    def do_command(self, e, cmd):  
        c = self.connection  
        displayname = e.tags[3].get('value')

        # Provide basic information to viewers for specific commands        
        if cmd == '테스트':
            message = "이 채팅이 보인다면 테스트가 제대로 진행되고 있다는 뜻이겠죠?"
            c.privmsg(self.channel, message)  

  
        # 리퀘스트 명령어 테스트
        elif cmd == '신청':

            global request_number
            global song_name

            print(len(e.arguments[0])) # 명령어 전체의 길이 파악
            
            if userlist.count(displayname) > 0:
                c.privmsg(self.channel, "한 사람당 한 곡만 신청할 수 있어요 T^T")

            else:
                if len(e.arguments[0]) > 3:
                    song_name.insert(request_number, e.arguments[0][4:]) # +리퀘스트 이후부터의 내용을 변수에 저장
                    print(song_name[request_number]) # 제대로 들어갔는지 테스트용
                    c.privmsg(self.channel, "대기열에 " + str(request_number + 1) + "번째 리퀘스트 >> " + str(song_name[request_number]) + " << (이)가 추가되었습니다.")
                    request_number += 1
                    print(request_number) # 전역변수 값이 제대로 수정되었나 출력용도
                    userlist.insert(request_number, displayname)

                else:
                    c.privmsg(self.channel, "정상적인 입력이 아닙니다 T^T")


        elif cmd == 'request':

            print(len(e.arguments[0])) # 명령어 전체의 길이 파악
            
            if userlist.count(displayname) > 0:
                c.privmsg(self.channel, "한 사람당 한 곡 이상 신청할 수 없어요 T^T")

            else:
                if len(e.arguments[0]) > 6:
                    song_name.insert(request_number, e.arguments[0][9:]) # +리퀘스트 이후부터의 내용을 변수에 저장
                    print(song_name[request_number]) # 제대로 들어갔는지 테스트용
                    c.privmsg(self.channel, "Add Request Queue, " + str(song_name[request_number]))
                    request_number += 1
                    print(request_number) # 전역변수 값이 제대로 수정되었나 출력용도
                    userlist.insert(request_number, displayname)

                else:
                    c.privmsg(self.channel, "정상적인 입력이 아닙니다 T^T")


#        elif cmd == '목록':
#            print(song_name)

#            if song_name != []:
#                c.privmsg(self.channel, "현재 신청되어 있는 곡은 " + str(song_name) + "입니다!")

#            else:
#                c.privmsg(self.channel, "현재 신청된 곡이 없어요 ㅠㅠ")


        # 정의되지 않은 커맨드가 입력 되었을때
        else:  
            c.privmsg(self.channel, "알수없는 명령어: " + cmd)
        




def main():  

    username = "" 
    client_id = "" # Client ID  
    token = "" # oauth 적어주면 됩니다.
    channel = "" # 봇이 접속할 채널입니다. 테스트할 땐 본인의 트위치 계정을 적어주세요.
  
    bot = TwitchBot(username, client_id, token, channel)  
    bot.start()  
    
if __name__ == "__main__":  
    main()