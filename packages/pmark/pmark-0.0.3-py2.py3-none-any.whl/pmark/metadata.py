import json
import munch
metadata = munch.Munch(json.load(open('/'.join(str(__file__).split('/')[:-1])+'/metadata.json')))
