--varlist '=' explist
a, b = 1, 2;

--functioncall
print(a, b);

--WHILE exp DO stmtlist END
while i == 2 do
    print(i);
    i = i + 1;
    j = "Hola";
end;

--IF exp THEN stmtlist elsepart END
if i <= 10 then
    print("Hola");
else
    print("Adios");
end;

--RETURN
return;

--RETURN explist
return true;

--BREAK
break;

--FOR NAME '=' exp ',' exp DO stmtlist END
for i = 2, 10 do
    print(8);
end;

--FOR NAME '=' exp ',' exp ',' exp DO stmtlist END
for i = 2, 10, 2 do
    print(4);
end;

--FOR namelist IN explist DO stmtlist END
for i in 2,3,4,5 do
    print(i);
end;

--FUNCTION function
function print(x)
    io.out(x);
end;

--LOCAL FUNCTION function
local function print(x)
    io.out(x);
end;

--LOCAL namelist
local c, d, e;

--LOCAL varlist '=' explist
local f, g = 6, 7;

--ELSEIF exp THEN stmtlist elsepart
if i <= 10 then
    print("Hola");
elseif i == 0 then
    print("nuse");
else
    print("Adios");
end;

--prefixexp '[' exp ']'
print(a[0]);

--True False Nil String
T = not true;
F = false;
N = nil;
S = "str";

--fieldlist
a = {[0] = 1, H = 2, [1 + 2] = 3};