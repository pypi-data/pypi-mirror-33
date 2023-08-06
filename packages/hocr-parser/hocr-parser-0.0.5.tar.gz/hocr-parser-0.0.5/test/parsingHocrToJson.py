from hocr_parser.parser import hocr_to_json
import json
dic = hocr_to_json('./testHocr.hocr')
j = json.dumps(dic, ensure_ascii=False,indent=4)
print(j)