from mosaicode.model.port import Port

class Bool(Port):

    def __init__(self):
        Port.__init__(self)
        self.language = "javascript"
        self.hint = "BOOL"
        self.color = "#2c6300"
        self.multiple = True
        self.code = "$output$.push($input$);\n"
        self.var_name = "$block[label]$_$block[id]$_$port[name]$"
