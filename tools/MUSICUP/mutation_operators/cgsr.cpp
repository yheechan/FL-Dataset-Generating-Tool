#include "../music_utility.h"
#include "cgsr.h"

bool CGSR::ValidateDomain(const std::set<std::string> &domain)
{
	for (auto e: domain)
    if (!IsValidVariableName(e))
      return false;

  return true;
}

bool CGSR::ValidateRange(const std::set<std::string> &range)
{
	return true;
}

void CGSR::setRange(std::set<std::string> &range)
{
  for (auto it = range.begin(); it != range.end(); )
  {
    if (HandleRangePartition(*it))
      it = range.erase(it);
    else
      ++it;
  }

  range_ = range;

  // for (auto it: partitions)
  //   cout << "part: " << it << endl;

  // for (auto it: range_)
  //   cout << "range: " << it << endl;
}

// Return True if the mutant operator can mutate this expression
bool CGSR::IsMutationTarget(clang::Expr *e, MusicContext *context)
{
	if (!ExprIsDeclRefExpr(e) || !ExprIsScalar(e))
		return false;

	SourceLocation start_loc = e->getBeginLoc();
	SourceLocation end_loc = GetEndLocOfExpr(e, context->comp_inst_);
	StmtContext &stmt_context = context->getStmtContext();

  SourceManager &src_mgr = context->comp_inst_->getSourceManager();
  Rewriter rewriter;
  rewriter.setSourceMgr(src_mgr, context->comp_inst_->getLangOpts());

  string token{ConvertToString(e, context->comp_inst_->getLangOpts())};
  bool is_in_domain = domain_.empty() ? true : 
                      IsStringElementOfSet(token, domain_);

  for(auto l_value_arg: (*(context->getSymbolTable()->getLValueArgList()))){
		SourceLocation start_loc_l = l_value_arg->getBeginLoc();
		SourceLocation end_loc_l = GetEndLocOfExpr(l_value_arg, context->comp_inst_);
		if(start_loc_l == start_loc && end_loc_l == end_loc){
			// cout<<"wozhengdemeiyouwenti"<<endl;
			// cout<<"expr: "<<ConvertToString(e, context->comp_inst_->getLangOpts())<<endl;
			return false;
		}
	}

	// CGSR can mutate scalar-type Declaration Reference Expression
	// inside mutation range, outside enum declaration, array decl size
	// (vulnerable to different uncompilable cases) and outside 
	// lhs of assignment, unary increment/decrement/addressop (these
	// cannot take constant literal as their target)
	return context->IsRangeInMutationRange(SourceRange(start_loc, end_loc)) &&
				 !stmt_context.IsInEnumDecl() &&
				 !stmt_context.IsInArrayDeclSize() &&
				 !stmt_context.IsInLhsOfAssignmentRange(e) &&
				 !stmt_context.IsInUnaryIncrementDecrementRange(e) &&
				 !stmt_context.IsInAddressOpRange(e) && is_in_domain;
}

void CGSR::Mutate(clang::Expr *e, MusicContext *context)
{
	SourceLocation start_loc = e->getBeginLoc();
	SourceLocation end_loc = GetEndLocOfExpr(e, context->comp_inst_);

	string token{ConvertToString(e, context->comp_inst_->getLangOpts())};

  vector<string> range;
  GetRange(e, context, &range);

  auto Canonicaltype = (e->getType()).getCanonicalType();

  for (auto it: range){
    if(ExprIsEnum(e)){
      string type_ = e->getType().getDesugaredType(context->comp_inst_->getASTContext()).getAsString();
      _BoolTobool(type_);
      auto ti{"static_cast<" + type_ + ">(" + it + ")"};
      it = ti;
    }
    if(const auto *BT = dyn_cast<BuiltinType>(Canonicaltype) ){
      if(BT->getKind() != BuiltinType::Int){
        string type_ = e->getType().getDesugaredType(context->comp_inst_->getASTContext()).getAsString();
        _BoolTobool(type_);
        auto ti{"static_cast<" + type_ + ">(" + it + ")"};
        it = ti;
      }
    }

    context->mutant_database_.AddMutantEntry(context->getStmtContext(),
        name_, start_loc, end_loc, token, it, 
        context->getStmtContext().getProteumStyleLineNum());
  }
}

void CGSR::GetRange(
    Expr *e, MusicContext *context, vector<string> *range)
{
  string token{ConvertToString(e, context->comp_inst_->getLangOpts())};
  StmtContext &stmt_context = context->getStmtContext();

  // cannot mutate the variable in switch condition or 
  // array subscript to a floating-type variable
  bool skip_float_literal = stmt_context.IsInArraySubscriptRange(e) ||
                            stmt_context.IsInSwitchStmtConditionRange(e) ||
                            stmt_context.IsInSwitchCaseRange(e) ||
                            stmt_context.IsInNonFloatingExprRange(e);

  vector<string> range_int;
  vector<string> range_float;

  for (auto it: *(context->getSymbolTable()->getGlobalScalarConstantList()))
  {
    string mutated_token{ConvertToString(it, context->comp_inst_->getLangOpts())};

    // Skip if this constant is not specified in range (if user specified range)
    if (!range_.empty() && !IsStringElementOfSet(mutated_token, range_))
      continue;

    // Skip float constants to avoid stillborn mutants.
    if (skip_float_literal && ExprIsFloat(it))
      continue;

    if (ExprIsFloat(it))
      ConvertConstFloatExprToFloatString(it, context->comp_inst_, mutated_token);
    else
      ConvertConstIntExprToIntString(it, context->comp_inst_, mutated_token);

    range->push_back(mutated_token);

    if (ExprIsFloat(it))
      range_float.push_back(mutated_token);
    else
      range_int.push_back(mutated_token);
  }

  // Return if user did not specify partition option
  if (partitions.size() == 0)
    return;

  range->clear();

  vector<long long> range_values_int;
  for (auto num: range_int)
  {
    long long val;
    try 
    {
      val = stoll(num);
    }
    catch(...) { continue; }

    range_values_int.push_back(val);
  }
  sort(range_values_int.begin(), range_values_int.end(), SortIntAscending);

  vector<long double> range_values_float;
  for (auto num: range_float)
  {
    long double val;
    try 
    {
      val = stold(num);
    }
    catch(...) { continue; }

    range_values_float.push_back(val);
  }
  sort(range_values_float.begin(), range_values_float.end(), SortFloatAscending);

  vector<string> range_values;
  MergeListsToStringList(range_values_int, range_values_float, range_values);

  // for (auto num: range_values)
  //   cout << "merged: " << num << endl;

  for (auto part_num: partitions) 
  {
    // Number of possible tokens to mutate to might be smaller than 10.
    // So we do not have 10 partitions.
    if (part_num > range_values.size())
    {
      cout << "There are only " << range_values.size() << " to mutate to.\n";
      cout << "No partition number " << part_num << endl;
      continue;
    }

    if (range_values.size() < num_partitions)
    {
      range->push_back(range_values[part_num-1]);
      continue;
    }

    int start_idx = (range_values.size() / 10) * (part_num - 1);
    int end_idx = (range_values.size() / 10) * part_num;

    if (part_num == 10)
      end_idx = range_values.size();

    for (int idx = start_idx; idx < end_idx; idx++)
      range->push_back(range_values[idx]);
  }

  // for (auto e: *range)
  //   cout << "range: " << e << endl;
}

bool CGSR::HandleRangePartition(string option) 
{
  vector<string> words;
  SplitStringIntoVector(option, words, string(" "));

  // Return false if this option does not contain enough words to specify 
  // partition or first word is not 'part'
  if (words.size() < 2 || words[0].compare("part") != 0)
    return false;

  for (int i = 1; i < words.size(); i++)
  {
    int num;
    if (ConvertStringToInt(words[i], num))
    {
      if (num > 0 && num <= 10)
        partitions.insert(num);
      else
      {
        cout << "No partition number " << num << ". Skip.\n";
        cout << "There are only 10 partitions for now.\n";
        continue;
      }
    }
    else
    {
      cout << "Cannot convert " << words[i] << " to an integer. Skip.\n";
      continue;
    }
  }

  return true;
}

void CGSR::MergeListsToStringList(vector<long long> &range_values_int,
                                  vector<long double> &range_values_float,
                                  vector<string> &range_values)
{
  int int_idx = 0;
  int float_idx = 0;

  while (int_idx < range_values_int.size() && 
         float_idx < range_values_float.size())
  {
    if (range_values_int[int_idx] > range_values_float[float_idx])
    {
      stringstream ss;
      ss << range_values_float[float_idx];
      range_values.push_back(ss.str());
      float_idx++;
    }
    else
    {
      range_values.push_back(to_string(range_values_int[int_idx]));
      int_idx++;
    }
  }

  while (int_idx < range_values_int.size())
  {
    range_values.push_back(to_string(range_values_int[int_idx]));
    int_idx++;
  }

  while (float_idx < range_values_float.size())
  {
    range_values.push_back(to_string(range_values_float[float_idx]));
    float_idx++;
  }  
}
