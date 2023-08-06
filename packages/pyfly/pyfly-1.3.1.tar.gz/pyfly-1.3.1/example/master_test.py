from pyfly import WebApp
import logging
logging.basicConfig(level = logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
x = WebApp()
x.run()