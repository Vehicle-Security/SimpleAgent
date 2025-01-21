#include<bits/stdc++.h>
using namespace std;
#define MAXN 3030

int n = 0;
int a[MAXN] = { 0 };

int main(){
	cin >> n;
	for(int i = 1; i <= n; i++) cin >> a[i];
	for(int i = 2; i <= n; i++) a[1] &= a[i];
	if(a[1] == 0) cout << "Yes\n";
	else cout << "No\n";
	return 0;
}

