__author__ = 'tlo'

from selenium import webdriver

import aws53
import dbdata
import homedns

db = dbdata.DbData()
query = db.getcurrent()

router = webdriver.Chrome("/home/tlo/Downloads/chromedriver")
# router = webdriver.PhantomJS()
# router.set_window_size(1120, 550)
router.implicitly_wait(30)

for (name, url1, namefield, namekeys, pwdfield, pwdkeys,
     btnname, url2, selector, address, routerid, timestamp) in query:

    router.get(url1)

    if url1[0:5] == 'https':
        router.find_element_by_name(namefield).send_keys(namekeys)
        router.find_element_by_name(pwdfield).send_keys(pwdkeys)
        router.find_element_by_id(btnname).click()
        router.get(url2)
        router_address = router.find_elements_by_css_selector(selector)[0].text
    else:
        router.find_element_by_id(namefield).send_keys(namekeys)
        router.find_element_by_id(pwdfield).send_keys(pwdkeys)
        router.find_element_by_id(btnname).click()
        router.get(url2)
        router_address = router.find_element_by_xpath(selector).text.rstrip(' /32')

    if router_address != address:
        aws53.update(name, router_address)
        db.savenew(routerid, router_address)

    dnsaddress = homedns.lookup(name)

    if router_address != dnsaddress[0].address:
        homedns.dnsupdate(dnsaddress, name)

router.close()
db.close()