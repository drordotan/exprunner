<!DOCTYPE html>
<html>
  <head>
    <title>${title}</title>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
${imports}
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

        //-- Allows aligning all RTs to a fixed offset
        let time0 = 0;

        // Code for saving results in case this is needed

        function generateCSVFile() {
            var data = jsPsych.data.get();
            data = data.filterCustom(function(trial) {
${filter_trials_func};
            });
            results_filename = ${results_filename};
            data.response_raw = data.response

            for (var trial_index = 0; trial_index < data.trials.length; trial_index++) {
                data.trials[trial_index].rt -= time0;
            }

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

${preload_sounds}

${instructions}

${play_start_of_session_beep}

${trials}


${trial_flow}


        //---------------------------
        //-- Start the experiment! --
        //---------------------------

        jsPsych.run(timeline);

  </script>
</html>
