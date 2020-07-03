from matplotlib.pyplot import axes, text, xlim, plot, legend, show
from matplotlib.lines import Line2D
from pandas import read_excel, DataFrame
from re import findall
from tkinter import *
from tkinter import Tk, BooleanVar, IntVar, StringVar, Checkbutton, Radiobutton, filedialog
from tkinter import W, E, BOTH, DISABLED, HORIZONTAL
from tkinter.ttk import Frame, Button, Label, Style, Scale


class Dialogue(Frame):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.style = Style()
        self.style.theme_use("default")
        self.master.title("LineChart")

        self.pack(fill=BOTH, expand=True)

        self.SSU = BooleanVar()
        self.SSU.set(1)
        self.COX1 = BooleanVar()
        self.COX1.set(1)
        self.EF1A = BooleanVar()
        self.EF1A.set(1)
        self.EF1A_variants = BooleanVar()
        self.EF1A_variants.set(1)
        self.filelabel = StringVar(self, "File not chosen")
        self.filename = ""
        self.var = IntVar()
        self.var.set(1)
        self.clades = IntVar()
        self.clades.set(0)

        # self.columnconfigure(2, weight=1)
        # self.rowconfigure(2, weight=1)

        cbSSU = Checkbutton(self, text="SSU", variable=self.SSU, state=DISABLED, onvalue=1, offvalue=0)
        cbSSU.select()
        cbSSU.grid(sticky=W, padx=5, pady=5)
        cbCOX1 = Checkbutton(self, text="COX1", variable=self.COX1, onvalue=1, offvalue=0)
        cbCOX1.select()
        cbCOX1.grid(sticky=W, row=1, padx=5, pady=5)
        cbEF1A = Checkbutton(self, text="EF1A", variable=self.EF1A, onvalue=1, offvalue=0)
        cbEF1A.select()
        cbEF1A.grid(sticky=W, row=2, padx=5, pady=5)
        cbEcomb = Checkbutton(self, text="EF1A combinations", variable=self.EF1A_variants, onvalue=1, offvalue=0)
        cbEcomb.select()
        cbEcomb.grid(sticky=W, row=3, padx=5, pady=5)

        openButton = Button(self, text="Choose file", command=self.onOpen)
        openButton.grid(sticky=W, row=0, column=1, padx=5, pady=5)

        labFile = Label(self, textvariable=self.filelabel)
        labFile.grid(sticky=W, row=0, column=2, columnspan=2, padx=5, pady=5)

        closeButton = Button(self, text="Exit", command=self.quit)
        closeButton.grid(sticky=E, row=4, column=3, padx=5, pady=5)

        okButton = Button(self, text = "OK", command=self.onOK)
        okButton.grid(sticky=W, row=4, column=0, padx=5, pady=5)

    def onOpen(self):
        ftypes = [('Excel files', '*.xls, *.xlsx'), ('All files', '*')]
        dlg = filedialog.Open(self, filetypes=ftypes)
        file = dlg.show()
        if file != '':
            self.filelabel.set("Current file: " + file)
            self.filename = file
            self.readExcel(self.filename)

        self.columns = BooleanVar()
        self.columns.set(1)

        if self.filelabel.get() != "File not chosen":
            rboneColumn = Radiobutton(self, text="Arrange in 1 column",
                                    variable=self.columns, value=1, command=self.onClick)
            rboneColumn.grid(sticky=W, row=2, column=1, padx=5, pady=5)

            rb2Columns = Radiobutton(self, text="Arrange in 2 columns",
                                    variable=self.columns, value=0, command=self.onClick)
            rb2Columns.grid(sticky=W, row=3, column=1, padx=5, pady=5)

    def readExcel(self, filename):
        self.dataframe = read_excel(filename, index_col="Specimen")

        if self.clades.get() != 0:
            self.labClades.grid_remove()

        self.clades.set(len(set(self.dataframe.loc[: , "Clade"])))

        self.labClades = Label(self, text="Number of clades: " + str(self.clades.get()))
        self.labClades.grid(sticky=W, row=1, column=1, padx=5, pady=5)

    def onClick(self):
        if self.columns.get() == 0:
            self.scale = Scale(self, from_=1, to=self.clades.get() - 1,
                               command=self.onScale, orient=HORIZONTAL)
            self.scale.grid(sticky=W, row=3, column=2)

            self.labScale = Label(self, text="Number of clades in the first column: ")
            self.labScale.grid(sticky=W, row=2, column=2)

            self.ScaleVal = Label(self, textvariable=self.var)
            self.ScaleVal.grid(sticky=E, row=2, column=2)

        else:
            self.scale.grid_remove()
            self.labScale.grid_remove()
            self.ScaleVal.grid_remove()

    def onScale(self, val):
        v = int(float(val))
        self.var.set(v)
        # print(self.var.get())

    def onOK(self):
        dataframe = self.dataframe
        SSU = self.SSU.get()
        COX1 = self.COX1.get()
        EF1A = self.EF1A.get()
        EF1A_combinations = self.EF1A_variants.get()
        change = self.var.get()
        onecolumn = self.columns.get()

        # graphical parameters: distance between columns and lines of variants, total height etc.
        top = 200  # uppermost position
        xS = 1  # X position of SSU column on the graph
        xE = 2  # X position of EF1A column on the graph
        xC = 0  # X position of COX1 column on the graph
        cladeX = 3.3  # X position of clade names on the graph
        distance = 5  # distance between lines
        shift = 5  # distance between two columns

        vardict = {}
        ssu_set = set()
        ef1a_set = set()
        cox1_set = set()

        # Count the number of specimens for each clade that have a valid SSU and at least one other valid gene variant
        countdict = {}
        for specimen in dataframe.index.values:
            valid = 0
            if findall("[A-Za-z]", str(dataframe.loc[specimen, "SSU"])) == []:
                if EF1A and COX1:
                    if findall("[A-Za-z]", str(dataframe.loc[specimen, "EF1A"])) == [] or findall("[A-Za-z]", str(
                            dataframe.loc[specimen, "COX1"])) == []:
                        valid = 1
                elif EF1A:
                    if findall("[A-Za-z]", str(dataframe.loc[specimen, "EF1A"])) == []:
                        valid = 1
                elif COX1:
                    if findall("[A-Za-z]", str(dataframe.loc[specimen, "COX1"])) == []:
                        valid = 1
            if dataframe.loc[specimen, "Clade"] not in countdict:
                countdict[dataframe.loc[specimen, "Clade"]] = valid
            else:
                countdict[dataframe.loc[specimen, "Clade"]] += valid

        # build a dict of connections for every SSU variant, regardless of clades
        for i in dataframe.index.values:
            if findall("[A-Za-z]", str(dataframe.loc[i, "SSU"])) == []:  # choosing ony valid SSU variants
                if dataframe.loc[i, "SSU"] not in vardict:
                    vardict[dataframe.loc[i, "SSU"]] = {"SSU_count": 1, "EF1A": {},
                                                        "COX1": {}}  # adding new SSU variant into dictionary
                    ssu_set.add(dataframe.loc[i, "SSU"])
                else:
                    vardict[dataframe.loc[i, "SSU"]]["SSU_count"] += 1  # increasing SSU variant count
                if COX1:
                    if findall("[A-Za-z]", str(dataframe.loc[i, "COX1"])) == []:  # choosing ony valid COX1 variants
                        if dataframe.loc[i, "COX1"] not in vardict[dataframe.loc[i, "SSU"]]["COX1"]:
                            vardict[dataframe.loc[i, "SSU"]]["COX1"][
                                dataframe.loc[i, "COX1"]] = 1  # adding new COX1 variant
                            cox1_set.add(dataframe.loc[i, "COX1"])
                        else:
                            vardict[dataframe.loc[i, "SSU"]]["COX1"][
                                dataframe.loc[i, "COX1"]] += 1  # increasing COX1 variant count
                if EF1A and EF1A_combinations:
                    if "homozygous" in str(dataframe.loc[i, "EF1A_combinations"]) \
                            or "both" in str(dataframe.loc[i, "EF1A_combinations"]) \
                            and findall("[A-Za-z]", str(dataframe.loc[
                                                            i, "EF1A"])) == []:  # choosing ony homozygous EF1A variants or unique unknown heterozygous
                        if dataframe.loc[i, "EF1A"] not in vardict[dataframe.loc[i, "SSU"]]["EF1A"]:
                            vardict[dataframe.loc[i, "SSU"]]["EF1A"][
                                dataframe.loc[i, "EF1A"]] = 1  # adding new EF1A variant
                            ef1a_set.add(dataframe.loc[i, "EF1A"])
                        else:
                            vardict[dataframe.loc[i, "SSU"]]["EF1A"][
                                dataframe.loc[i, "EF1A"]] += 1  # increasing EF1A variant count

                    elif "+" in str(dataframe.loc[i, "EF1A_combinations"]):  # choosing known heterozygous variants
                        for var in findall("[0-9]+", str(dataframe.loc[i, "EF1A_combinations"])):
                            if var not in vardict[dataframe.loc[i, "SSU"]]["EF1A"]:
                                vardict[dataframe.loc[i, "SSU"]]["EF1A"][var] = 1  # adding new EF1A variant
                                ef1a_set.add(int(var))
                            else:
                                vardict[dataframe.loc[i, "SSU"]]["EF1A"][var] += 1  # increasing EF1A variant count
                elif EF1A and findall("[A-Za-z]", str(dataframe.loc[i, "EF1A"])) == []:
                    if dataframe.loc[i, "EF1A"] not in vardict[dataframe.loc[i, "SSU"]]["EF1A"]:
                        vardict[dataframe.loc[i, "SSU"]]["EF1A"][dataframe.loc[i, "EF1A"]] = 1  # adding new EF1A variant
                        ef1a_set.add(dataframe.loc[i, "EF1A"])
                    else:
                        vardict[dataframe.loc[i, "SSU"]]["EF1A"][
                            dataframe.loc[i, "EF1A"]] += 1  # increasing EF1A variant count

        # print(vardict)

        # # modify dataframe by adding known heterozygous variants into EF1A column.

        new_dataframe = dataframe

        if EF1A_combinations:
            for i in range(len(new_dataframe["EF1A_combinations"])):
                if "+" in str(new_dataframe["EF1A_combinations"][i]):
                    if len(findall("[0-9]+", str(new_dataframe["EF1A_combinations"][i]))) == 1:
                        new_dataframe.loc[new_dataframe.index.values[i], "EF1A"] = int(
                            findall("[0-9]+", str(new_dataframe["EF1A_combinations"][i]))[0])
                    elif len(findall("[0-9]+", str(new_dataframe["EF1A_combinations"][i]))) == 2:
                        new_dataframe.loc[new_dataframe.index.values[i], "EF1A"] = int(
                            findall("[0-9]+", str(new_dataframe["EF1A_combinations"][i]))[0])
                        new_dataframe = new_dataframe.append(new_dataframe.iloc[i], ignore_index=True)
                        new_dataframe.loc[new_dataframe.index.values[-1], "EF1A"] = int(
                            findall("[0-9]+", str(new_dataframe["EF1A_combinations"][i]))[1])
                        new_dataframe.loc[new_dataframe.index.values[-1], "COX1"] = ""

        grouping_columns = ["Clade", "SSU"]
        if COX1:
            grouping_columns.append("COX1")
        if EF1A:
            grouping_columns.append("EF1A")

        grouped = new_dataframe.groupby(grouping_columns).aggregate({"SSU": "count"})
        # print(grouped)

        # starting Y coordinates
        yS = top
        yE = top
        yC = top

        # dictionaries with pairs of coordinates for every variant of every gene
        ssu_coo = {}
        cox1_coo = {}
        ef1a_coo = {}
        clade_coo = {}

        # sets of clades and variants that were catalogued already to avoid duplicates
        clade_done = set()
        ssu_done = set()
        cox1_done = set()
        ef1a_done = set()

        # Gives XY coordinates to every genetic variant iterating through clades.
        # Variants are sorted acending; clades are sorted alphabetically
        counter = 0

        # adjusting distance between columns by adding the size of the longest clade name length
        shift_adj = 0.1 * max([len(i) for i in grouped.index.get_level_values("Clade")]) + 0.3
        shift += shift_adj

        for clade in grouped.index.get_level_values("Clade"):
            if clade not in clade_done:
                if not onecolumn and counter == change:  # if a specified change value is reached, starts the second column with a specified shift
                    xS += shift
                    yS = top
                    if COX1:
                        xC += shift
                        yC = top
                    if EF1A:
                        xE += shift
                        yE = top
                    cladeX += shift

                counter += 1

                yS -= distance
                if COX1:
                    yC -= distance
                if EF1A:
                    yE -= distance

                # add coordinates of the clade name and vertical line at the side
                ssuvalid = set([i for i in grouped.loc[(clade)].index.get_level_values("SSU")
                                if findall("[A-Za-z]", str(i)) == []
                                and str(i) != ""])
                if COX1:
                    cox1valid = set([i for i in grouped.loc[(clade)].index.get_level_values("COX1")
                                     if findall("[A-Za-z]", str(i)) == []
                                     and str(i) != ""])

                if EF1A:
                    ef1avalid = set([i for i in grouped.loc[(clade)].index.get_level_values("EF1A")
                                     if findall("[A-Za-z]", str(i)) == []
                                     and str(i) != ""])

                genelenlist = [len(ssuvalid)]
                if COX1:
                    genelenlist.append(len(cox1valid))
                if EF1A:
                    genelenlist.append(len(ef1avalid))

                cladeY = yS - (max(genelenlist) - 1) * distance * 0.5
                linestart = yS + 0.5 * distance
                lineend = yS - (max(genelenlist) - 1) * distance - 0.5 * distance
                clade_coo[clade] = [cladeX, cladeY, cladeX - 0.2, linestart, lineend, countdict[clade]]

                # within-clade vertical position adjustments
                if COX1 and not EF1A:
                    if len(ssuvalid) - len(cox1valid) >= 2:
                        yC -= distance * (len(ssuvalid) - len(cox1valid)) // 2
                    elif len(cox1valid) - len(ssuvalid) >= 2:
                        yS -= distance * (len(cox1valid) - len(ssuvalid)) // 2

                elif EF1A and COX1:
                    if len(ssuvalid) - len(cox1valid) >= 2:
                        yC -= distance * (len(ssuvalid) - len(cox1valid)) // 2
                        if len(ssuvalid) - len(ef1avalid) >= 2:
                            yE -= distance * (len(ssuvalid) - len(ef1avalid)) // 2
                        elif len(ef1avalid) - len(ssuvalid) >= 2:
                            yS -= distance * (len(ef1avalid) - len(ssuvalid)) // 2
                            yC -= distance * (len(ef1avalid) - len(ssuvalid)) // 2

                    elif len(cox1valid) - len(ssuvalid) >= 2:
                        yS -= distance * (len(cox1valid) - len(ssuvalid)) // 2
                        if len(cox1valid) - len(ef1avalid) >= 2:
                            yE -= distance * (len(cox1valid) - len(ef1avalid)) // 2
                        elif len(ef1avalid) - len(cox1valid) >= 2:
                            yC -= distance * (len(ef1avalid) - len(cox1valid)) // 2
                            yS -= distance * (len(ef1avalid) - len(cox1valid)) // 2

                    elif len(ef1avalid) - len(ssuvalid) >= 2:
                        yS -= distance * (len(ef1avalid) - len(ssuvalid)) // 2
                        yC -= distance * (len(ef1avalid) - len(cox1valid)) // 2

                    elif len(ssuvalid) - len(ef1avalid) >= 2:
                        yE -= distance * (len(ssuvalid) - len(ef1avalid)) // 2

                elif EF1A:
                    if len(ssuvalid) - len(ef1avalid) >= 2:
                        yE -= distance * (len(ssuvalid) - len(ef1avalid)) // 2
                    elif len(ef1avalid) - len(ssuvalid) >= 2:
                        yS -= distance * (len(ef1avalid) - len(ssuvalid)) // 2

                # finally, assign coordinates
                for ssu in grouped.loc[(clade)].index.get_level_values("SSU"):
                    if findall("[A-Za-z]", str(ssu)) == [] and str(
                            ssu) != "":  # choose only valid genetic variants (no text, only numbers)
                        if ssu not in ssu_done:
                            ssu_coo[ssu] = [xS, yS]
                            yS -= distance

                        ssu_done.add(ssu)
                if COX1:
                    for cox1 in grouped.loc[(clade)].index.get_level_values("COX1"):
                        if findall("[A-Za-z]", str(cox1)) == [] and str(
                                cox1) != "":  # choose only valid genetic variants (no text, only numbers)
                            if cox1 not in cox1_done:
                                cox1_coo[cox1] = [xC, yC]
                                yC -= distance
                            cox1_done.add(cox1)
                if EF1A:
                    for ef1a in grouped.loc[(clade)].index.get_level_values("EF1A"):
                        if findall("[A-Za-z]", str(ef1a)) == [] and str(
                                ef1a) != "":  # choose only valid genetic variants (no text, only numbers)
                            if ef1a not in ef1a_done:
                                ef1a_coo[ef1a] = [xE, yE]
                                yE -= distance
                            ef1a_done.add(ef1a)

            clade_done.add(clade)

            geneXlist = [xS]
            geneYlist = [yS]
            if COX1:
                geneXlist.append(xC)
                geneYlist.append(yC)
            if EF1A:
                geneXlist.append(xE)
                geneYlist.append(yE)

            lowest = min(geneYlist)

            yS = lowest
            yC = lowest
            yE = lowest

        # print(grouped)

        # Building a plot

        def choose_line(size):  # a rule for choosing line width for the plot
            size = int(size)
            if size in (1, 2):
                width = 1
            elif size == 3:
                width = 1.5
            elif size < 6:
                width = 2
            elif size < 11:
                width = 2.5
            else:
                width = 3
            return width

        # remove axes
        ax1 = axes(frameon=False)
        ax1.set_frame_on(False)
        ax1.get_xaxis().set_visible(False)
        ax1.get_yaxis().set_visible(False)

        # build the lines between genetic variants
        for ssu in vardict:
            if EF1A:
                for ef1a in vardict[ssu]["EF1A"]:
                    if findall("[A-Za-z]", str(ef1a)) == []:
                        size = vardict[ssu]["EF1A"][ef1a]
                        plot([ef1a_coo[int(ef1a)][0] + 0.4, ssu_coo[ssu][0] + 0.5],
                             [ef1a_coo[int(ef1a)][1], ssu_coo[ssu][1]],
                             linestyle="dashed" if size == 1 else "solid",
                             linewidth=choose_line(size),
                             color="black")
                        text(ef1a_coo[int(ef1a)][0] + 0.7, ef1a_coo[int(ef1a)][1], ef1a, ha="center", va="center")
            if COX1:
                for cox1 in vardict[ssu]["COX1"]:
                    if findall("[A-Za-z]", str(cox1)) == []:
                        size = vardict[ssu]["COX1"][cox1]
                        plot([cox1_coo[cox1][0], ssu_coo[ssu][0]],
                             [cox1_coo[cox1][1], ssu_coo[ssu][1]],
                             linestyle="dashed" if size == 1 else "solid",
                             linewidth=choose_line(vardict[ssu]["COX1"][cox1]),
                             color="black")
                        text(cox1_coo[cox1][0] - 0.3, cox1_coo[cox1][1], cox1, ha="center", va="center")
            text(ssu_coo[ssu][0] + 0.25, ssu_coo[ssu][1], ssu, ha="center", va="center")

        # add gene names above the variants for the second column

        if not onecolumn:
            text(xS - shift + 0.25, top + distance + 0.2, "SSU", ha="center")
            text(xS + 0.25, top + distance + 0.2, "SSU", ha="center")
            if EF1A:
                text(xE - shift + 0.7, top + distance + 0.2, "EF1A", ha="center")
                text(xE + 0.7, top + distance + 0.2, "EF1A", ha="center")
            if COX1:
                text(xC - shift - 0.3, top + distance + 0.2, "COI", ha="center")
                text(xC - 0.3, top + distance + 0.2, "COI", ha="center")
        else:
            text(xS + 0.25, top + distance + 0.2, "SSU", ha="center")
            if EF1A:
                text(xE + 0.7, top + distance + 0.2, "EF1A", ha="center")
            if COX1:
                text(xC - 0.3, top + distance + 0.2, "COI", ha="center")

        # add clade names and vertical lines to the right of the column
        for clade in clade_coo:
            if EF1A:
                text(clade_coo[clade][0], clade_coo[clade][1],
                     "%s (%d)" % (clade, clade_coo[clade][5]),
                     ha="left", va="center")

                plot([clade_coo[clade][2], clade_coo[clade][2]],
                     [clade_coo[clade][3], clade_coo[clade][4]],
                     linewidth=2,
                     color="black")
            else:
                text(clade_coo[clade][0] - shift * 0.5 + shift_adj + 0.65,
                     clade_coo[clade][1],
                     "%s (%d)" % (clade, clade_coo[clade][5]),
                     ha="left", va="center")

                plot([clade_coo[clade][2] - shift * 0.5 + shift_adj + 0.7,
                      clade_coo[clade][2] - shift * 0.5 + shift_adj + 0.7],
                     [clade_coo[clade][3], clade_coo[clade][4]],
                     linewidth=2,
                     color="black")

        # set limits for X axis to avoid overlapping with legend
        if not onecolumn and EF1A:
            xlim(0, 14)
        elif not onecolumn:
            xlim(0, 12)
        elif onecolumn and EF1A:
            xlim(0, 7)
        elif onecolumn:
            xlim(0, 5)

        # produce lines for a legend
        leg_lines = [Line2D([0], [0], color="black", linestyle="dashed", linewidth=1),
                     Line2D([0], [0], color="black", linewidth=1),
                     Line2D([0], [0], color="black", linewidth=1.5),
                     Line2D([0], [0], color="black", linewidth=2),
                     Line2D([0], [0], color="black", linewidth=2.5),
                     Line2D([0], [0], color="black", linewidth=3)]

        # plot legend
        legend(leg_lines, ["1", "2", "3", "4-5", "6-10", "11-20"], loc="upper right")

        # show the plot
        show()


def main():
    root = Tk()
    app = Dialogue()
    root.mainloop()


if __name__ == '__main__':
    main()
