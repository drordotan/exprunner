<!DOCTYPE html>
<html>
  <head>
    <title>${title}</title>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <script src="jspsych/jspsych.js"></script>
    <script src="jspsych/plugins/jspsych-html-keyboard-response.js"></script>
    <link href="jspsych/css/jspsych.css" rel="stylesheet" type="text/css">

	<style>
${layout_css}
	</style>
  </head>
  <body></body>

  <script>

    let timeline = [];

${instructions}


${trials}


${trial_flow}




    /* start the experiment */
    jsPsych.init({
      timeline: timeline,
${on_finish}
    });

  </script>
</html>
