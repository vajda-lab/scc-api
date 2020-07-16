let colors = {
  "crosscluster.000":"#00FFFF",
  "crosscluster.001":"#0000FF",
  "crosscluster.002":"#8A2BE2",
  "crosscluster.003":"#DC143C",
  "crosscluster.004":"#FF7F50",
  "crosscluster.005":"#FF1493",
  "crosscluster.006":"#9400D3",
  "crosscluster.007":"#7FFF00",
  "crosscluster.008":"#191970",
  "crosscluster.009":"#008000",
  "crosscluster.010":"#FF0000",
  "crosscluster.011":"#FFFF00",
  "crosscluster.012":"#FF00FF",
  "crosscluster.013":"#FFD700",
  "crosscluster.014":"#7FFFD4",
  "crosscluster.015":"#F0FFF0",
  "consensus.000":"#00FFFF",
  "consensus.001":"#0000FF",
  "consensus.002":"#8A2BE2",
  "consensus.003":"#DC143C",
  "consensus.004":"#FF7F50",
  "consensus.005":"#FF1493",
  "consensus.006":"#9400D3",
  "consensus.007":"#7FFF00",
  "consensus.008":"#191970",
  "consensus.009":"#008000",
  "consensus.010":"#FF0000",
  "consensus.011":"#FFFF00",
  "consensus.012":"#FF00FF",
  "consensus.013":"#FFD700",
  "consensus.014":"#7FFFD4",
  "consensus.015":"#F0FFF0",
};


function split_pdb(data) {
  let parts = data.split(/HEADER (.*)\n/);
  let components = new Map();

  for (let i = 1; i < parts.length; i += 2) {
    components.set(parts[i], parts[i + 1]);
  }

  return components;
}

function update_ngl(new_file) {

  $.get(new_file, function(data) {
    let components = split_pdb(data);

    for (let [key, value] of components) {
      let blob = new Blob([value], {
        type: 'text/plain'
      });

      //main protein
      if (key === 'protein') {
        stage.loadFile(blob, {
          ext: 'pdb'
        }).then(function(output) {
          output.addRepresentation("cartoon", {
            color: "atomindex"
          });
          output.autoView();
        });
      }

      // crossclusters
      else {
        // get the key for colors
        let cluster = key.slice(0,-4);
        // add to stage
        stage.loadFile(blob, {
          ext: 'pdb'
        }).then(function(output) {
          output.addRepresentation("ball+stick", {
            color: colors[cluster]
          });
        });
      }
    }
  });

  $("canvas").addClass("img-thumbnail");
}
