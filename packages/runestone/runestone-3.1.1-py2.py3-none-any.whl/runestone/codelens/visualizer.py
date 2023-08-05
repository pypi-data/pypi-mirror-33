# Copyright (C) 2011  Bradley N. Miller
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

__author__ = 'bmiller'

from docutils import nodes
from docutils.parsers.rst import directives
from .pg_logger import exec_script_str_local
import json
import six
from runestone.server.componentdb import addQuestionToDB, addHTMLToDB
from runestone.common.runestonedirective import RunestoneIdDirective

def setup(app):
    app.add_directive('codelens', Codelens)
    app.add_stylesheet('pytutor.css')
    app.add_stylesheet('modal-basic.css')

    app.add_javascript('d3.v2.min.js')
    app.add_javascript('jquery.ba-bbq.min.js')
    app.add_javascript('jquery.jsPlumb-1.3.10-all-min.js')
    app.add_javascript('pytutor.js')
    app.add_javascript('codelens.js')

    app.add_config_value('codelens_div_class', "alert alert-warning cd_section", 'html')


VIS = '''
<div class="runestone" style="max-width: none;">
<div class="%(divclass)s">
<div id="%(divid)s"></div>
<p class="cl_caption"><span class="cl_caption_text">%(caption)s (%(divid)s)</span> </p>
</div>'''

QUESTION = '''
<div id="%(divid)s_modal" class="modal fade codelens-modal">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h4 class="modal-title">Check your understanding</h4>
      </div>
      <div class="modal-body">
        <p>%(question)s</p>
        <input id="%(divid)s_textbox" type="textbox" class="form-control" style="width:200px;" />
        <br />
        <button id="%(divid)s_tracecheck" class='btn btn-default tracecheck' onclick="traceQCheckMe('%(divid)s_textbox','%(divid)s','%(correct)s')">
          Check Me
        </button>
        <button type="button" class="btn btn-default" data-dismiss="modal">Continue</button>
        <br />
        <p id="%(divid)s_feedbacktext" class="feedbacktext alert alert-warning"></p>
      </div>
    </div>
  </div>
</div>

'''

DATA = '''
<script type="text/javascript">
%(tracedata)s
var %(divid)s_vis;

$(document).ready(function() {
    try {
        %(divid)s_vis = new ExecutionVisualizer('%(divid)s',%(divid)s_trace,
                                    {embeddedMode: %(embedded)s,
                                    verticalStack: false,
                                    heightChangeCallback: redrawAllVisualizerArrows,
                                    codeDivWidth: 500,
                                    lang : '%(python)s'
                                    });
        attachLoggers(%(divid)s_vis,'%(divid)s');
        styleButtons('%(divid)s');
        allVisualizers.push(%(divid)s_vis);
    } catch (e) {
        console.log("Failed to Initialize CodeLens component %(divid)s_vis" );
        console.log(e.toString());
    }

});

$(document).ready(function() {
    $("#%(divid)s_tracecheck").click(function() {
        logBookEvent({'event':'codelens', 'act': 'check', 'div_id':'%(divid)s'});
    });
});

if (allVisualizers === undefined) {
   var allVisualizers = [];
}


$(window).resize(function() {
    if (%(divid)s_vis) {
        %(divid)s_vis.redrawConnectors();
    }
});
</script>
</div>
'''


# Some documentation to help the author.
# Here's and example of a single stack frame.
# you might ask a qestion about the value of a global variable
# in which case the correct answer is expressed as:
#
# globals.a
#
# You could ask about a value on the heap
#
# heap.variable
#
# You could ask about a local variable -- not shown here.
#
# locals.variable
#
# You could even ask about what line is going to be executed next
#
# line
# {
#   "ordered_globals": [
#     "a",
#     "b"
#   ],
#   "stdout": "1\n",
#   "func_name": "<module>",
#   "stack_to_render": [],
#   "globals": {
#     "a": 1,
#     "b": 1
#   },
#   "heap": {},
#   "line": 5,
#   "event": "return"
# }


class Codelens(RunestoneIdDirective):
    """
.. codelens:: uniqueid
   :tracedata: Autogenerated or provided
   :caption: caption below
   :showoutput: show stdout from program
   :question: Text of question to ask on breakline
   :correct: correct answer to the question
   :feedback: feedback for incorrect answers
   :breakline: Line to stop on and pop up a question dialog
   :python: either py2 or py3

    x = 0
    for i in range(10):
       x = x + i


config values (conf.py): 

- codelens_div_class - custom CSS class of the component's outermost div
    """
    required_arguments = 1
    optional_arguments = 1
    option_spec = RunestoneIdDirective.option_spec.copy()
    option_spec.update({
        'tracedata': directives.unchanged,
        'caption': directives.unchanged,
        'showoutput': directives.flag,
        'question': directives.unchanged,
        'correct': directives.unchanged,
        'feedback': directives.unchanged,
        'breakline': directives.nonnegative_int,
        'python': directives.unchanged
    })

    has_content = True

    def run(self):
        super(Codelens, self).run()

        addQuestionToDB(self)

        self.JS_VARNAME = ""
        self.JS_VARVAL = ""

        def raw_dict(input_code, output_trace):
            ret = dict(code=input_code, trace=output_trace)
            return ret

        def js_var_finalizer(input_code, output_trace):
            global JS_VARNAME
            ret = dict(code=input_code, trace=output_trace)
            json_output = json.dumps(ret, indent=None)
            return "var %s = %s;" % (self.JS_VARNAME, json_output)

        if self.content:
            source = "\n".join(self.content)
        else:
            source = '\n'

        CUMULATIVE_MODE = False
        self.JS_VARNAME = self.options['divid'] + '_trace'
        env = self.state.document.settings.env
        self.options['divclass'] = env.config.codelens_div_class

        if 'showoutput' not in self.options:
            self.options['embedded'] = 'true'  # to set embeddedmode to true
        else:
            self.options['embedded'] = 'false'

        if 'python' not in self.options:
            if six.PY2:
                self.options['python'] = 'py2'
            else:
                self.options['python'] = 'py3'

        if 'question' in self.options:
            curTrace = exec_script_str_local(source, None, CUMULATIVE_MODE, None, raw_dict)
            self.inject_questions(curTrace)
            json_output = json.dumps(curTrace, indent=None)
            self.options['tracedata'] = "var %s = %s;" % (self.JS_VARNAME, json_output)
        else:
            self.options['tracedata'] = exec_script_str_local(source, None,
                                                              CUMULATIVE_MODE,
                                                              None, js_var_finalizer)

        res = VIS
        if 'caption' not in self.options:
            self.options['caption'] = ''
        if 'question' in self.options:
            res += QUESTION
        if 'tracedata' in self.options:
            res += DATA
        else:
            res += '</div>'
        addHTMLToDB(self.options['divid'], self.options['basecourse'], res % self.options)
        raw_node = nodes.raw(self.block_text, res % self.options, format='html')
        raw_node.source, raw_node.line = self.state_machine.get_source_and_line(self.lineno)
        return [raw_node]

    def inject_questions(self, curTrace):
        if 'breakline' not in self.options:
            raise RuntimeError('Must have breakline option')
        breakline = self.options['breakline']
        for frame in curTrace['trace']:
            if frame['line'] == breakline:
                frame['question'] = dict(text=self.options['question'],
                                         correct=self.options['correct'],
                                         div=self.options['divid'] + '_modal',
                                         feedback=self.options['feedback'])
