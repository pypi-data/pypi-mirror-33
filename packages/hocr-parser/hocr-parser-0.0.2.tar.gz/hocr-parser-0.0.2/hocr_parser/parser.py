from lxml import html
import os
import json
import traceback
import logging
import sys

# class hocr_to_json:
#     def __init__(self):
#         super().__init__()

def hocr_to_json(hocr_file_path):
        f = None
        doc = None
        final_response = {}
        try:
            with open(hocr_file_path, 'r') as f:
                doc = html.parse(f)
            response_dic = {}
            responses_list = []
            textAnnotations_list = []
            parXY = {"minX":"0","minY":"0","maxX":"0","maxY":"0"}

            pars = doc.xpath("//*[@class='ocr_par']")
            full_str = ""
            for par_idx, par in enumerate(pars):
                par_locale = par.get('lang')
                par_bbox = par.get('title').split(';')[0].split(" ")
                if (par_idx == 0):
                    parXY["minX"] = par_bbox[1]
                    parXY["minY"] = par_bbox[2]
                    parXY["maxX"] = par_bbox[3]
                    parXY["maxY"] = par_bbox[4]
                    initXY = False

                if(int(parXY.get('minX')) > int(par_bbox[1])):
                    parXY["minX"] = par_bbox[1]
                if(int(parXY.get('minY')) > int(par_bbox[2])):
                    parXY["minY"] = par_bbox[2]
                if(int(parXY.get('maxX')) < int(par_bbox[3])):
                    parXY["maxX"] = par_bbox[3]
                if(int(parXY.get('maxY')) < int(par_bbox[4])):
                    parXY["maxY"] = par_bbox[4]

                lines = par.xpath("./*[@class='ocr_line']")
                for line_idx, line in enumerate(lines):
                    # print(line.text_content())
                    full_str = full_str + line.text_content()
                    words = line.xpath("./*[@class='ocrx_word']")
                    for word_idx, word in enumerate(words):
                        word_dic = {}
                        textAnnotation_dic = {}
                        boundingPloy_dic = {}
                        vertices_list = []

                        textAnnotation_dic["description"] = word.text_content()

                        bbox = word.get('title').split(";")[0].split(" ")

                        minX = bbox[1]
                        minY = bbox[2]
                        maxX = bbox[3]
                        maxY = bbox[4]

                        vertice_dic = {}
                        vertice_dic["x"] = minX
                        vertice_dic["y"] = minY
                        vertices_list.append(vertice_dic)

                        vertice_dic = {}
                        vertice_dic["x"] = maxX
                        vertice_dic["y"] = minY
                        vertices_list.append(vertice_dic)

                        vertice_dic = {}
                        vertice_dic["x"] = maxX
                        vertice_dic["y"] = maxY
                        vertices_list.append(vertice_dic)

                        vertice_dic = {}
                        vertice_dic["x"] = minX
                        vertice_dic["y"] = maxY
                        vertices_list.append(vertice_dic)
                        # print(vertices_list)
                        boundingPloy_dic["vertices"] = vertices_list
                        textAnnotation_dic["boundingPoly"] = boundingPloy_dic
                        textAnnotations_list.append(textAnnotation_dic)
            boundingPloy_dic = {}
            textAnnotation_dic = {}
            vertices_list = []
            vertice_dic = {}
            vertice_dic["x"] = parXY.get("minX")
            vertice_dic["y"] = parXY.get("minY")
            vertices_list.append(vertice_dic)
            vertice_dic = {}
            vertice_dic["x"] = parXY.get("maxX")
            vertice_dic["y"] = parXY.get("minY")
            vertices_list.append(vertice_dic)
            vertice_dic = {}
            vertice_dic["x"] = parXY.get("maxX")
            vertice_dic["y"] = parXY.get("maxY")
            vertices_list.append(vertice_dic)
            vertice_dic = {}
            vertice_dic["x"] = parXY.get("minX")
            vertice_dic["y"] = parXY.get("maxY")
            vertices_list.append(vertice_dic)
            boundingPloy_dic["vertices"] = vertices_list

            textAnnotation_dic["locale"] = par_locale
            textAnnotation_dic["description"] = full_str
            textAnnotation_dic["boundingPoly"] = boundingPloy_dic
            textAnnotations_list.insert(0,textAnnotation_dic)

            response_dic["textAnnotations"] = textAnnotations_list
            responses_list.append(response_dic)
            final_response["responses"] = responses_list
            print(final_response)
                    # str = str+word.get('title')
                    # print(line.text_content())
                    # print(line_idx)
        except IOError as e:
            logging.error(traceback.format_exc())
            return
        return final_response





