from medium import mediumScraper
import os

# set working directory
os.chdir('/Users/benediktbosch/Desktop')

# Institute of Supply Chain Management, 30.06.2020

keyword = 'covid'
filename = 'medium_covid_Q3'
start = '01-07-2020'
finish = '30-09-2020'

# done
ms = mediumScraper(keyword, filename, start, finish)
ms.run()

# done
# cs = conversationScraper(keyword, filename, start, finish)
# cs.run()

# done
# tw = twitterScraper(keyword, filename, start, finish)
# tw.run()

# scmr = scmrScraper(keyword, filename, start, finish)
# scmr.run()

# done
# scbrain = scbrainScraper(keyword, filename, start, finish)
# scbrain.run()

# done
# spendmatters = spendmattersScraper(keyword, filename, start, finish)
# spendmatters.run()

# done
# nlpa = nlpaScraper(keyword, filename, start, finish)
# nlpa.run()

# done
# sc247 = sc247Scraper(keyword, filename, start, finish)
# sc247.run()

# adjustment needed
# procurious = procuriousScraper(keyword, filename, start, finish)
# procurious.run()