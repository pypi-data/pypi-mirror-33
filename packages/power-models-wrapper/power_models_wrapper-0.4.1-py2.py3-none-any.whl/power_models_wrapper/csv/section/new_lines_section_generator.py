class NewLinesSectionGenerator():

    def write_rows_for_new_lines(self, writer, data):

        new_lines_header_row = [""]
        new_lines_header_row += ["node" + str(i + 1) for i in range(len(data))]
        writer.writerow(new_lines_header_row)

        data_rows = [["node" + str(i + 1)] + row_list for i, row_list in enumerate(data.tolist())]
        for data_row in data_rows:
            writer.writerow(data_row)
