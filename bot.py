import time
import telebot
import requests
import sys

from gram import credentials
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class Bot:

    def __init__(self, username, password):
        self.browserProfile = webdriver.ChromeOptions()
        self.browserProfile.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        if(sys.platform == 'Win32' or 'Win64'):
            self.browser = webdriver.Chrome(executable_path=r'C:\Users\jlind\Dropbox\Projects\gram\chromedriver.exe',
                                        options=self.browserProfile)
        else:
            self.browser = webdriver.Chrome(executable_path=r'/Users/jakelindsey/Dropbox/Projects/gram/chromedriver',
                                            options=self.browserProfile)
        self.username = username
        self.password = password
        self.isLoggedIn = False

    def login(self):
        self.browser.get('https://www.instagram.com/accounts/login/')

        usernameInput = self.browser.find_elements_by_css_selector('form input')[0]
        passwordInput = self.browser.find_elements_by_css_selector('form input')[1]

        usernameInput.send_keys(self.username)
        passwordInput.send_keys(self.password)
        passwordInput.send_keys(Keys.ENTER)
        self.isLoggedIn = True
        time.sleep(2)

    def profile(self):
        self.browser.get('https://www.instagram.com/' + credentials.INSTAGRAM_USERNAME)

    def followWithUsername(self, username):
        self.browser.get('https://www.instagram.com/' + username + '/')
        time.sleep(2)
        followButton = self.browser.find_element_by_css_selector('button')
        if (followButton.text != 'Following'):
            followButton.click()
            time.sleep(2)
        else:
            print("You are already following this user")

    def unfollowWithUsername(self, username):
        self.browser.get('https://www.instagram.com/' + username + '/')
        time.sleep(2)
        followButton = self.browser.find_element_by_css_selector('button')
        if (followButton.text == 'Following'):
            followButton.click()
            time.sleep(2)
            confirmButton = self.browser.find_element_by_xpath('//button[text() = "Unfollow"]')
            confirmButton.click()
        else:
            print("You are not following this user")

    def getUserFollowers(self, username, max):
        self.browser.get('https://www.instagram.com/' + username)
        followersLink = self.browser.find_element_by_css_selector('ul li a')
        followersLink.click()
        time.sleep(2)
        followersList = self.browser.find_element_by_css_selector('div[role=\'dialog\'] ul')
        numberOfFollowersInList = len(followersList.find_elements_by_css_selector('li'))

        followersList.click()
        actionChain = webdriver.ActionChains(self.browser)
        while (numberOfFollowersInList < max):
            actionChain.key_down(Keys.SPACE).key_up(Keys.SPACE).perform()
            numberOfFollowersInList = len(followersList.find_elements_by_css_selector('li'))
            print(numberOfFollowersInList)

        followers = []
        for user in followersList.find_elements_by_css_selector('li'):
            userLink = user.find_element_by_css_selector('a').get_attribute('href')
            print(userLink)
            followers.append(userLink)
            if (len(followers) == max):
                break
        return followers

    def closeBrowser(self):
        self.browser.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.closeBrowser()


def main():

    telegramBot = telebot.TeleBot(credentials.TELEGRAM_TOKEN)
    instagramBot = Bot(credentials.INSTAGRAM_USERNAME, credentials.INSTAGRAM_PASSWORD)

    profile_page = "https://instagram.com/{}"
    hashtags = ['sherpa']
    id_list = []

    def initPost(message):
        telegramBot.reply_to(message, 'Dx5 @' + credentials.INSTAGRAM_USERNAME + '\n' + credentials.INSTAGRAM_PICTURE)

    def find_at(msg):
        for i in msg:
            if '@' in i:
                return i

    def find_link(msg):
        for i in msg:
            if 'https' in i:
                return i

    def check_if_active(url):
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        if 'Page Not Found' in soup.title.text:
            return False
        else:
            return True

    @telegramBot.message_handler(func=lambda msg: msg.text is not None and "@" in msg.text)
    def at_converter(message):
        texts = message.text.split()
        at_text = find_at(texts)
        if at_text == '@':
            pass
        else:
            profile_page.format(at_text[1:])
            if check_if_active(profile_page):
                telegramBot.reply_to(message, profile_page)
            else:
                pass

    # @telegramBot.message_handler(commands=["setmode"])
    # def gram(message):
    #     telegramBot.(message, 'Mode: ' + mode + " selected.")
    # make another function to display modes after login with descriptions

    @telegramBot.message_handler(commands=["login"])
    def gram(message):
        telegramBot.reply_to(message, 'Please wait, I am attempting to log you in...')
        instagramBot.login()

        if instagramBot.isLoggedIn:
            loginStatus = 'I have successfully logged you in.'
        else:
            loginStatus = 'Invalid username or password, please check credentials.'

        telegramBot.reply_to(message, loginStatus)

        mode = 1

        if mode == 1:
            for i in range(len(id_list)):
                if len(id_list) == i:
                    telegramBot.reply_to(message, 'Finished liking from file.')
                else:
                    tag = id_list[0]
                    instagramBot.likeTele(tag)
                    id_list.remove(tag)
            initPost(message)
            instagramBot.profile()
        elif mode == 2:
            instagramBot.likeTag(hashtags)
        elif mode == 3:
            # instaBot.commentTele(tag)
            print('Mode 3 not developed yet.')
        elif mode == 4:
            # instaBot.lc(tag, comment)
            print('Mode 4 not developed yet.')
        elif mode == 5:
            print('Mode 5 not developed yet.')
        else:
            telegramBot.reply_to(message, 'The mode you selected does not exist.')

    @telegramBot.message_handler(commands=["open"])
    def read(message):
        count = 0
        with open("DATABASE.txt", "r") as f:
            while True:
                link_list = f.readline().splitlines()
                image_page = find_link(link_list)
                if image_page is None:
                    break
                else:
                    ext = format(image_page[28:39])
                    id_list.append(ext)
                    telegramBot.reply_to(message, "[Dx" + str(count + 1) + "]: " + image_page)
                    count += 1
                    if count == 10:
                        break

    while True:
        try:
            telegramBot.polling(none_stop=True)
        except Exception:
            time.sleep(15)


if __name__ == '__main__':
    main()
