// Part 1: the same job in JavaScript (Node 18 or newer).
const URL_TEMPLATE = "https://date.nager.at/api/v3/PublicHolidays";

async function fetchHolidays(year, country = "PH") {
  // Ask the server for JSON and turn it into arrays and objects.
  const response = await fetch(`${URL_TEMPLATE}/${year}/${country}`);
  return response.json();
}

function isWeekday(holiday) {
  const day = new Date(`${holiday.date}T00:00:00`).getDay();
  return day !== 0 && day !== 6;
}

function formatHoliday(holiday) {
  return `${holiday.date}  ${holiday.name}`;
}

async function main() {
  const year = Number(process.argv[2] ?? 2027);
  const holidays = await fetchHolidays(year);
  const weekdayHolidays = holidays.filter(isWeekday);
  for (const holiday of weekdayHolidays) {
    console.log(formatHoliday(holiday));
  }
  console.log(`${weekdayHolidays.length} of ${holidays.length} holidays fall on a school day.`);
}

if (require.main === module) {
  main();
}

module.exports = { fetchHolidays, isWeekday, formatHoliday };
