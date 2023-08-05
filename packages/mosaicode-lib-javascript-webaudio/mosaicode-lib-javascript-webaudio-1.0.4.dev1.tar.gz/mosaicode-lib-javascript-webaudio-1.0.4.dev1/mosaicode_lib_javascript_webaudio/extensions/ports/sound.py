from mosaicode.model.port import Port

class Sound(Port):

    def __init__(self):
        Port.__init__(self)
        self.language = "javascript"
        self.hint = "SOUND"
        self.color = "#F00"
        self.multiple = True
        self.code = "$output$.connect($input$);\n"
        self.var_name = "$block[label]$_$block[id]$_$port[name]$"
