from flask import Flask, render_template
app = Flask (__name__)

@app.route("/dashboard")
def dashboard():

	data= {
		"main_repo_name" : "Main Project Name",
		"main_repo_summary" : "Summary: This project is about making Zebra really fast and efficient",
		"main_repo_description" : "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
		"heatmap" : {
			"divID" : "heatmap",
			"title" : "Commits by Hour of Week - dummy data",
			"data_path1" : "../static/data/data_dummy.tsv",
			"data_path2" : "../static/data/data2_dummy.tsv",
			"summary" : "This data shows cool stuff",
			"description" : "As you van see, this data focuses on business hours",
			"timestamp" : "System last updated at 11:34am"
		},
		"barchart" : {
			"divID" : "day_of_week",
			"title" : "# Commits by day - real data",
			"data_path" : "../static/data/day_of_week_copy.tsv",
			"summary" : "Bar Chart",
			"description" : "What week is this from? Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
			"timestamp" : "System last updated at 11:34am"
		},
		"linegraph1" : {
			"divID" : "lineChart1",
			"title" : "Commits per Author - real data",
			"data_path" : "../static/data/commits_by_author_copy.tsv",
			"summary" : "Multi Series Line Chart",
			"description" : "Theres a few authors on this project but 1 stands out",
			"timestamp" : "System last updated at 11:34am"
		},
		"linegraph2" : {
			"divID" : "lineChart2",
			"title" : "Commits per Author - real data",
			"data_path" : "../static/data/lines_of_code_by_author_copy.tsv",
			"summary" : "Multi Series Line Chart",
			"description" : "Theres a few authors on this project but 1 stands out",
			"timestamp" : "System last updated at 11:34am"
		}
	}
	return render_template("dashboard.html", data=data )



if __name__ == "__main__":
	app.run()

