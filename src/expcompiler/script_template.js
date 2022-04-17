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

    let timeline = [];

    //init jsPsych
    ${init_jsPsych}

${instructions}


${trials}


${trial_flow}




    /* start the experiment */
    jsPsych.run(timeline);

  </script>
</html>
