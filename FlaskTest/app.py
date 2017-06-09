from flask import Flask, render_template
app = Flask (__name__)


data= {
	"main_repo" : 
	[{
		"name" : "Simul-scan",
		"summary" : "Summary: This project is about making Zebra really fast and efficient",
		"description" : "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
		"visualizations" : 
		[
			{
				"heatmap" : {
					"divID" : "heatmap",
					"title" : "Commits by Hour of Week - dummy data",
					# NOTE these paths are relative to where the script.js file is
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
		]
	}],

	"sub_repos" : 
	[
		# each of these is going to be a sub-repo
		{
			"name" : "sub-1",
			"summary" : "Test Summary1",
			"description" : "Test Description 1",
			"visualizations" : 
			[
				{
					"heatmap" : {
						"divID" : "heatmap",
						"title" : "Commits by Hour of Week - dummy data",
						# NOTE these paths are relative to where the script.js file is
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
			]
		},
		{
			"name" : "sub-2",
			"summary" : "Test Summary 2",
			"description" : "Test Description 2",
			"visualizations" : 
			[
				{
					"heatmap" : {
						"divID" : "heatmap",
						"title" : "Commits by Hour of Week - dummy data",
						# NOTE these paths are relative to where the script.js file is
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
			]
		}
	]
}

@app.route('/dashboard/<repo>')	
def sub_repo(repo):
	global data
	sub_repo_data= None
	for sub_repo in data['sub_repos']:
		print (sub_repo['name'], repo)
		if sub_repo['name'] == repo:
			#this should happen in one case, else this isnt a valid sub repo...
			sub_repo_data=sub_repo
	return render_template("dashboard.html", sub=sub_repo_data, nav=data)

@app.route("/dashboard")
def dashboard():
	global data
	main_repo=data['main_repo'][0]
	return render_template("dashboard.html", sub=main_repo, nav=data )




if __name__ == "__main__":
	app.run()

