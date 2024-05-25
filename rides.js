    // `map` over the first object in the array
// and get an array of keys and add them
// to TH elements
const formatHeading = (key) => {
  if (typeof value === 'boolean') {
    return value ? '✅' : '❌'
  }

  if (typeof value === 'string' && value.indexOf('http') >= 0) {
    return <a class="pathlink" href={value}>link</a>;
  }
  if (key == 'distance_in_km') {
    return 'KM';
  }
  if (key == 'duration_in_hours') {
    return 'Hours';
  }

  return key;
}

function getHeadings(data) {
  return Object.keys(data[0]).map(key => {
    return <th>{formatHeading(key)}</th>;
  });
}

// `map` over the data to return
// row data, passing in each mapped object
// to `getCells`
function getRows(data) {
  return data.map(obj => {
    return <tr>{getCells(obj)}</tr>;
  });
}

const formatEntry = (key, value) => {
  if (typeof value === 'boolean') {
    return value ? '✅' : '❌'
  }

  if (typeof value === 'string' && value.indexOf('http') >= 0) {
    return <a class="pathlink" href={value}>link</a>;
  }

  if (key == 'path') {
    const orig = value[0]['place']['latitude'] + ',' + value[0]['place']['longitude'];
    const dest = value[1]['place']['latitude'] + ',' + value[1]['place']['longitude'];
    return <a class='direction' origin={orig} destination={dest}>🔎</a>;
  }

  return value;
}

// Return an array of cell data using the
// values of each object
function getCells(obj) {
  return Object.entries(obj).map(([key, value]) => {
    return <td>{formatEntry(key, value)}</td>;
  });
}

// Simple component that gets the
// headers and then the rows
function Example({ data }) {
  return (
    <table>
      <thead>{getHeadings(data)}</thead>
      <tbody>{getRows(data)}</tbody>
    </table>
  );
}

function RenderRides( data ) {
  ReactDOM.render(
      <Example data={data} />,
      document.getElementById('react')
  );

  $('.direction').click(function() {
    const orig = $(this).attr('origin');
    const dest = $(this).attr('destination');
    $('#mapframe').attr("src", 
      "https://www.google.com/maps/embed/v1/directions?key=x" + 
      "&origin=" + orig +
      "&destination=" + dest);
  });
  $('.direction')[0].click();
}