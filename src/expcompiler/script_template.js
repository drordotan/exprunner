<!DOCTYPE html>
<html>
  <head>
    <title>${title}</title>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <script src="https://unpkg.com/jspsych@7.1.2"></script>
    <script src="https://unpkg.com/@jspsych/plugin-html-keyboard-response@1.1.0"></script>
    <script src="https://unpkg.com/@jspsych/plugin-html-button-response@1.1.0"></script>
    <link href="https://unpkg.com/jspsych@7.1.2/css/jspsych.css" rel="stylesheet" type="text/css" />

	<style>
${layout_css}
	</style>
  </head>
  <body></body>

  <script>

        //---------------------
        //-- URL parameters  --
        //---------------------

${url_parameters}

        //------------------------
        //-- initialize jsPsych --
        //------------------------

        // Code for saving results in case this is needed

        function generateCSVFile() {
            var data = jsPsych.data.get();
            data = data.filterCustom(function(trial) {
${filter_trials_func};
            });
            results_filename = ${results_filename};
            data.response_raw = data.response
            data.ignore('internal_node_id').ignore('trial_type').ignore('stimulus').ignore('response').localSave('csv', results_filename);
        }

        function on_jspsych_finish() {
            generateCSVFile();

            const downloadLink = document.createElement("a");
            downloadLink.appendChild(document.createTextNode("Click here to re-download the results."))
            downloadLink.href = "#";

            downloadLink.addEventListener("click", generateCSVFile);

            const jspsychContent = document.getElementById("jspsych-content")

            if (jspsychContent) {
                jspsychContent.appendChild(downloadLink);
            }
            else {
                document.body.prepend(downloadLink);
            }
        }

        let jsPsych = initJsPsych(${init_jspsych_params});


        //--------------------------------
        //-- Create experiment timeline --
        //--------------------------------

        let timeline = [];

${instructions}


${trials}


${trial_flow}


        //---------------------------
        //-- Start the experiment! --
        //---------------------------

        jsPsych.run(timeline);

  </script>
</html>
