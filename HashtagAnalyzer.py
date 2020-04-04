import json
import click
import arrow
from bokeh.plotting import figure, show, output_file

@click.command()
@click.argument('filename')
@click.argument('hashtag')
def analyze_hashtag(hashtag, filename):
    with open(filename, "r") as f:
        data = json.load(f)['GraphImages']

    start_timestamp = data[-1]['taken_at_timestamp']
    end_timestamp = data[0]['taken_at_timestamp']

    start = arrow.get(start_timestamp)
    end = arrow.get(end_timestamp)

    print(f"DATA COLLECTED FROM FILE {filename} ON #{hashtag} from {start.format('YYYY-MM-DD')} to {end.format('YYYY-MM-DD')}")
    analyze(data, hashtag)
    
    year_clusters = cluster_data_by("year", data)
    for year in sorted(map(lambda x: int(x), year_clusters)):            
        print(f"DATA COLLECTED FROM YEAR {year}")
        analyze(year_clusters[str(year)], hashtag)
    
    output_file("data.html")
    month_clusters = cluster_data_by("month", data)
    month_timestamps_and_counts = list(map(lambda x: (arrow.get(x).datetime, len(month_clusters[x])), month_clusters))
    month_timestamps_and_counts.sort(key=lambda x: x[0])
    x_axis_data = list(map(lambda x: x[0], month_timestamps_and_counts))
    y_axis_data = list(map(lambda x: x[1], month_timestamps_and_counts))

    plot = figure(
        x_axis_type="datetime",
        x_axis_label="Month",
        y_axis_label="Number of posts with the hashtag",
        tooltips=[("Posts", "@top")]
    )

    plot.vbar(x=x_axis_data, top=y_axis_data, fill_color="blue", legend_label=f"#{hashtag}", width=2629743 * 800)

    show(plot)
    
def analyze(data, hashtag):
    max_tags_to_analyze = 30

    hashtag_count, total_tags = get_all_hashtags(data)
    total_tags -= hashtag_count[hashtag]
    del hashtag_count[hashtag]

    size_list = list(map(lambda x: (x, hashtag_count[x]), hashtag_count))
    size_list.sort(key=lambda x: x[1], reverse=True)

    print(f"\tTotal number of posts: {len(data)}")
    print(f"\tTotal number of hashtags in the posts (excluding analyzed one): {total_tags}")
    print(f"\tTotal number of unique hashtags: {len(size_list)}")
    print(f"Data for the {max_tags_to_analyze} most common tags:")
    most_common_total = 0
    for tag in size_list[0:max_tags_to_analyze]:
        most_common_total += tag[1]
        print(f"\t#{tag[0]} appeared {tag[1]} times")
    print(f"\tAll other tags appeared a total of {total_tags-most_common_total} times\n\n")



def cluster_data_by(period, data):
    result = {}
    filtered = filter(lambda x: 'tags' in x, data)
    for item in filtered:
        time = arrow.get(item['taken_at_timestamp'])
        if period == "year":
            date = time.format("YYYY")
        elif period == "month":
            date = time.format("YYYY-MM")
        else:
            raise ValueError("period can only be month or year")
        existing_data = result.get(date, [])
        existing_data.append(item)
        result[date] = existing_data

    return result

    
def get_all_hashtags(data):
    result = {}
    total = 0
    filtered = filter(lambda x: 'tags' in x, data)
    for item in filtered:
        for tag in item['tags']:
            count = result.get(tag, 0)
            result[tag] = count + 1
            total += 1
    
    return result, total


if __name__ == "__main__":
    analyze_hashtag()