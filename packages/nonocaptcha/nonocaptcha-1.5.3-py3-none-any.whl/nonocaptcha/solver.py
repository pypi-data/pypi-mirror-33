#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Solver module."""

import asyncio
import json
import pathlib
import time
import sys

from asyncio import TimeoutError, CancelledError
from pyppeteer.util import merge_dict
from user_agent import generate_navigator_js

from config import settings
from nonocaptcha.base import Base, Detected, SafePassage, Success
from nonocaptcha.audio import SolveAudio
from nonocaptcha.image import SolveImage
from nonocaptcha.launcher import Launcher
from nonocaptcha import util


class ButtonError(Exception):
    pass
    
class DefaceError(Exception):
    pass


class Solver(Base):
    browser = None
    launcher = None
    proc_count = 0
    proc = None

    def __init__(
        self,
        pageurl,
        sitekey,
        proxy=None,
        proxy_auth=None,
        options={},
        **kwargs,
    ):
        self.options = merge_dict(options, kwargs)
        self.url = pageurl
        self.sitekey = sitekey
        self.proxy = proxy
        self.proxy_auth = proxy_auth

        self.headless = settings["headless"]
        self.gmail_accounts = {}
        self.proc_id = self.proc_count
        type(self).proc_count += 1

    async def start(self):
        """Begin solving"""

        result = None
        start = time.time()
        try:
            self.browser = await self.get_new_browser()
            target = [t for t in self.browser.targets() if await t.page()][0]
            self.page = await target.page()
            if self.proxy_auth:
                await self.page.authenticate(self.proxy_auth)

            if settings["gmail"]:
                await self.sign_in_to_google()

            self.log(f"Starting solver with proxy {self.proxy}")
            result = await self.solve()
        except CancelledError as e:
            raise e
        except BaseException as e:
            self.log(f"{e} {type(e)}")
        finally:
            end = time.time()
            elapsed = end - start
            self.log(f"Time elapsed: {elapsed}")
            if self.browser:
                await self.browser.close()
        return result

    async def get_new_browser(self):
        """Get new browser, set arguments from options, proxy,
        and random window size if headless.
        """

        chrome_args = []
        if self.proxy:
            chrome_args.append(f"--proxy-server=http://{self.proxy}")

        args = self.options.pop("args")
        args.extend(chrome_args)
        self.options.update({"headless": self.headless, "args": args})

        self.launcher = Launcher(self.options)
        browser = await self.launcher.launch()
        return browser

    async def cloak_navigator(self):
        """Emulate another browser's navigator properties and set webdriver
            false, inject jQuery.
        """

        jquery_js = await util.load_file(settings["data_files"]["jquery_js"])
        override_js = await util.load_file(
            settings["data_files"]["override_js"]
        )
        navigator_config = generate_navigator_js(
            os=("linux", "mac", "win"), navigator=("chrome")
        )
        navigator_config["webdriver"] = False
        dump = json.dumps(navigator_config)
        _navigator = f"const _navigator = {dump};"
        await self.page.evaluateOnNewDocument(
            "() => {\n%s\n%s\n%s}" % (_navigator, jquery_js, override_js)
        )
        return navigator_config["userAgent"]

    async def wait_for_deface(self):
        """Overwrite current page with reCAPTCHA widget and wait for image
        iframe to load on document before continuing.

        Function x is an odd hack for multiline text, but it works.
        """

        html_code = await util.load_file(settings["data_files"]["deface_html"])
        deface_js = (
            (
                """() => {
    var x = (function () {/*
        %s
    */}).toString().match(/[^]*\/\*([^]*)\*\/\}$/)[1];
    document.open();
    document.write(x)
    document.close();
}
"""
                % html_code
            )
            % self.sitekey
        )
        await self.page.evaluate(deface_js)
        func = """() => {
    frame = $("iframe[src*='api2/bframe']")
    $(frame).load( function() {
        window.ready_eddy = true;
    });
    if(window.ready_eddy) return true;
}"""
        timeout = settings["wait_timeout"]["deface_timeout"]
        await self.page.waitForFunction(func, timeout=timeout * 1000)

    async def goto_and_deface(self):
        """Open tab and deface page"""

        user_agent = await self.cloak_navigator()
        await self.page.setUserAgent(user_agent)
        try:
            timeout = settings["wait_timeout"]["load_timeout"]
            await self.page.goto(
                self.url, timeout=timeout * 1000, waitUntil="documentloaded"
            )
            await self.wait_for_deface()
        except TimeoutError:
            raise DefacetError("Problem defacing page")

    async def solve(self):
        """Clicks checkbox, on failure it will attempt to solve the audio
        file
        """

        if settings["check_blacklist"]:
            await self.is_blacklisted()

        await self.goto_and_deface()
        self.get_frames()
        # await self.wait_for_checkbox()
        await self.click_checkbox()
        timeout = settings["wait_timeout"]["success_timeout"]
        try:
            await self.check_detection(self.checkbox_frame, timeout=timeout)
        except Detected:
            raise
        except SafePassage:
            return await self._solve()
        except Success:
            code = await self.g_recaptcha_response()
            if code:
                return code

    async def _solve(self):
        # Coming soon...
        solve_image = False
        if solve_image:
            self.image = SolveImage(self.page, self.proxy, self.proc_id)
            solve = self.image.solve_by_image
        else:
            self.audio = SolveAudio(self.page, self.proxy, self.proc_id)
            await self.wait_for_audio_button()
            await self.click_audio_button()
            solve = self.audio.solve_by_audio

        try:
            await solve()
        except Success:
            code = await self.g_recaptcha_response()
            if code:
                return code

    async def wait_for_checkbox(self):
        """Wait for audio button to appear."""

        timeout = settings["wait_timeout"]["audio_button_timeout"]
        try:
            await self.image_frame.waitForFunction(
                "$('#recaptcha-anchor').length", timeout=timeout * 1000
            )
        except ButtonError:
            raise ButtonError("Checkbox missing, aborting")

    async def click_checkbox(self):
        """Click checkbox on page load."""

        if settings["keyboard_traverse"]:
            self.body = await self.page.J("body")
            await self.body.press("Tab")
            await self.body.press("Enter")
        else:
            self.log("Clicking checkbox")
            checkbox = await self.checkbox_frame.J("#recaptcha-anchor")
            await self.click_button(checkbox)

    async def wait_for_audio_button(self):
        """Wait for audio button to appear."""

        timeout = settings["wait_timeout"]["audio_button_timeout"]
        try:
            await self.image_frame.waitForFunction(
                "$('#recaptcha-audio-button').length", timeout=timeout * 1000
            )
        except ButtonError:
            raise ButtonError("Audio button missing, aborting")

    async def click_audio_button(self):
        """Click audio button after it appears."""

        if not settings["keyboard_traverse"]:
            self.log("Clicking audio button")
            audio_button = await self.image_frame.J("#recaptcha-audio-button")
            await self.click_button(audio_button)
        else:
            await self.body.press("Enter")

        timeout = settings["wait_timeout"]["audio_button_timeout"]
        try:
            await self.check_detection(self.image_frame, timeout)
        except Detected:
            raise
        except SafePassage:
            pass

    async def g_recaptcha_response(self):
        code = await self.page.evaluate("$('#g-recaptcha-response').val()")
        return code

    async def is_blacklisted(self):
        self.log("Checking Google search for blacklist")
        timeout = settings["wait_timeout"]["load_timeout"]
        url = "https://www.google.com/search?q=my+ip&hl=en"
        response = await util.get_page(url, proxy=self.proxy, timeout=timeout)
        detected_phrase = (
            "Our systems have detected unusual traffic " "from your computer"
        )
        if detected_phrase in response:
            raise Detected("IP has been blacklisted by Google")

    async def sign_in_to_google(self):
        cookie_path = settings["data_files"]["cookies"]
        if pathlib.Path(cookie_path).exists():
            self.gmail_accounts = await util.deserialize(cookie_path)
        if settings["gmail"] not in self.gmail_accounts:
            url = "https://accounts.google.com/Login"
            page = await self.browser.newPage()
            await page.goto(url, waitUntil="documentloaded")
            username = await page.querySelector("#identifierId")
            await username.type(settings["gmail"])
            button = await page.querySelector("#identifierNext")
            await button.click()
            await asyncio.sleep(2)  # better way to do this...
            password = await page.querySelector("#password")
            await password.type(settings["gmail_password"])
            button = await page.querySelector("#passwordNext")
            await button.click()
            await page.waitForNavigation()
            cookies = await page.cookies()
            self.gmail_accounts[settings["gmail"]] = cookies
            util.serialize(self.gmail_accounts, cookie_path)
            await page.close()
        await self.load_cookies()

    async def load_cookies(self, account=settings["gmail"]):
        cookies = self.gmail_accounts[account]
        for c in cookies:
            await self.page.setCookie(c)
