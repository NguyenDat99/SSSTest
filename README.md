# SSSTest

# Question 1
C#
```
int SumOfOddNumbers(int a, int b)
{
	if (a >= b) return 0;
	int first = a % 2 == 0 ? a + 1 : a + 2;
	int last = b % 2 == 0 ? b - 1 : b - 2;
	int totals = (last-first) / 2 + 1;
	string number1 = totals.ToString();
	string number2 = (first + totals - 1).ToString();
	// mul
	string result = "";
	if (number1 == "0" || number2 == "0") result = "0";
	number1 = string.Join("", number1.Reverse());
	number2 = string.Join("", number2.Reverse());
	List<int> current, previous = null;
	for (int i = 0; i < number1.Length; i++)
	{
		current = number2.Select(y => (y - '0') * (number1[i] - '0')).ToList();
		current.InsertRange(0, Enumerable.Repeat(0, i));
		if (previous != null)
			current = current.Select((x, j) => x + (j < previous.Count ? previous[j] : 0)).ToList();
		previous = current;
	}
	var tmp = new StringBuilder();
	int sum = 0, carry = 0;
	foreach (var x in previous)
	{
		sum = x + carry;
		carry = sum / 10;
		sum = sum % 10;
		tmp.Insert(0, sum);
	}
	if (carry > 0)
		tmp.Insert(0, carry);
	result= tmp.ToString();
	// div
	int finalResult = 0;
	for (int index = 0; index < result.Length; index++)
		finalResult = (finalResult * 10 + (int)result[index] - '0') % 10000007;
	return finalResult;
}
```

# Question 2

![Architecture](https://github.com/NguyenDat99/SSSTest/blob/main/Src/image.jpg)

Project structure
-----------------

Application parts are:
```
└── Src
    ├── ApiServer
    │   ├── static
    │   └── utils
    ├── WebApp
    │   ├── static
    │   │   ├── css
    │   │   ├── img
    │   │   ├── js
    │   │   ├── scss
    │   │   └── vendor  
    │   ├── templates
    │   └── utils
    └── Worker
        └── utils
```
First, clone source from github:
```
git clone https://github.com/NguyenDat99/SSSTest.git
```

To run the web application in debug use:
```
docker compose up -d
```

Web application server URL:
```
http://webhost.localhost
```

Web application API server URL:
```
http://webapi.localhost
```
Swagger:
```
http://webapi.localhost/swagger
```
API gateway dashboard:
```
http://webapi.localhost:8000
```
