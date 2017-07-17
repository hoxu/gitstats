set terminal png transparent size 640,240
set size 1.0,1.0

set terminal png transparent size 640,480
set output 'lines_of_code_by_author.png'
set key left top
set yrange [0:]
set xdata time
set timefmt "%s"
set format x "%Y-%m-%d"
set grid y
set ylabel "Lines"
set xtics rotate
set bmargin 6
plot 'lines_of_code_by_author.dat' using 1:2 title "Lawrence Ng" w lines, 'lines_of_code_by_author.dat' using 1:3 title "Neeta" w lines, 'lines_of_code_by_author.dat' using 1:4 title "Ted Trask" w lines, 'lines_of_code_by_author.dat' using 1:5 title "Neeta Joshi" w lines, 'lines_of_code_by_author.dat' using 1:6 title "Sachini Samarasinghe" w lines, 'lines_of_code_by_author.dat' using 1:7 title "Malinda Kandalama" w lines, 'lines_of_code_by_author.dat' using 1:8 title "Malinda" w lines
