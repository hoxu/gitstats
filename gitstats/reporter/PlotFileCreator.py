class PlotFileCreator(object):
    def __init__(self, conf, input, output, plot):
        self.conf = conf
        self.input = input
        self.output = output
        self.header = "set terminal png transparent size %s" % self.conf.image_resolution
        self.key = "unset key"
        self.yrange = "[0:]"
        self.xrange = ""
        self.grid = "y"
        self.ylabel = ""
        self.xlabel = ""
        self.xtics = ""
        self.xtics_rotate = True
        self.bmargin = 6
        self.timefmt = ""
        self.formatx = ""
        self.plot = plot
        self.plot_using = ""
        self.additional = ""

    def set_labels(self, xlabel, ylabel):
        self.xlabel = xlabel
        self.ylabel = ylabel

    def set_time_from_string(self, timefmt = None):
        if timefmt:
            self.formatx = timefmt
        else:
            self.formatx = self.conf.date_format
        self.timefmt = "%s"

    def set_time(self, timefmt):
        self.timefmt = timefmt
        self.formatx = timefmt

    def create(self):
        text = self.header + "\n"
        text += "set output '%s'\n" % self.output
        text += self.key + "\n"
        if self.xrange:
            text += "set xrange %s\n" % self.yrange
        if self.yrange:
            text += "set yrange %s\n" % self.yrange
        if "y" in self.grid:
            text += "set grid y\n"
        if "x" in self.grid:
            text += "set grid x\n"
        text += "set ylabel '%s'\n" % self.ylabel
        text += "set xlabel '%s'\n" % self.xlabel
        if self.xtics_rotate:
            text += "set xtics %s rotate\n" % self.xtics
        else:
            text += "set xtics %s rotate\n" % self.xtics
        if self.bmargin:
            text += "set bmargin %d\n" % self.bmargin
        if self.timefmt and self.formatx:
            text += "set xdata time\n"
            text += "set timefmt '%s'\n" % self.timefmt
            text += "set format x '%s'\n" % self.formatx
        text += self.additional + "\n"
        text += "plot %s %s\n" % (self.plot, self.plot_using)

        f = open(self.input, 'w')
        f.write(text)
        f.close()