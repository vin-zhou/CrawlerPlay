import csv
from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.globals import ChartType


class City:
    city_name = ''
    hot_value = 0


# 读取csv并把其转换成echart能够识别的数据类型
def load_file():
    with open("qunar.csv", "r") as csvfile:
        reader = csv.reader(csvfile)
        city_list = []
        # 逐行读取
        for line in reader:
            if len(line[0].split('·')) > 1:
                city = City()
                city.city_name = line[0].split('·')[1]
                city.hot_value = float(line[5].split(' ')[1])
                found_repeat_city = 0
                # 按城市热点求和
                for origin_city in city_list:
                    if origin_city.city_name == city.city_name:
                        origin_city.hot_value += city.hot_value
                        found_repeat_city = 1
                        break
                # 过滤掉城市没有在echart备案的信息
                if found_repeat_city == 0 \
                        and Geo().get_coordinate(name=city.city_name) is not None \
                        and int(city.hot_value) != 0:
                    city_list.append(city)
        # 生成输入信息，用来传入到echart中
        output_geo_data = []
        for city in city_list:
            output_geo_data_record = (city.city_name, int(city.hot_value * 5))
            output_geo_data.append(output_geo_data_record)
        print(output_geo_data)
    return output_geo_data


def geo_base(data) -> Geo:
    c = (
        # 初始化地理热力图
        Geo().add_schema(maptype="china")
            .add("2019热力图", data, ChartType.HEATMAP)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(),
            title_opts=opts.TitleOpts(title="2019热力图"))
    )
    return c


if __name__ == '__main__':
    data = load_file()
    geo_base(data).render()
