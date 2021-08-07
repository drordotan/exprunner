<!DOCTYPE html>
<html>
  <head>
    <title>${title}</title>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <script src="jspsych-6.2.0/jspsych.js"></script>
    <script src="jspsych-6.2.0/plugins/jspsych-html-keyboard-response.js"></script>
    <link href="jspsych-6.2.0/css/jspsych.css" rel="stylesheet" type="text/css">

	<style>
${layout_css}
	</style>
  </head>
  <body></body>

  <script>

    let timeline = [];

${instructions}

    const trial_data = [
${trials}
    ];

${trial_flow}

    timeline.push(trial_procedure);

    /* start the experiment */
    jsPsych.init({
      timeline: timeline,
${on_finish}
    });

  </script>
</html>
