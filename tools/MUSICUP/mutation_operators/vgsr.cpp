#include "../music_utility.h"
#include "vgsr.h"

bool VGSR::ValidateDomain(const std::set<std::string> &domain)
{
  for (auto e: domain)
    if (!IsValidVariableName(e))
      return false;

  return true;

	// return domain.empty();
}

bool VGSR::ValidateRange(const std::set<std::string> &range)
{
  // for (auto e: range)
  //   if (!IsValidVariableName(e))
  //     return false;

  return true;

	// return range.empty();
}

void VGSR::setRange(std::set<std::string> &range)
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
bool VGSR::IsMutationTarget(clang::Expr *e, MusicContext *context)
{
	if (!ExprIsScalarReference(e))
		return false;

	SourceLocation start_loc = e->getBeginLoc();
	SourceLocation end_loc = GetEndLocOfExpr(e, context->comp_inst_);
	StmtContext &stmt_context = context->getStmtContext();

  for(auto l_value_arg: (*(context->getSymbolTable()->getLValueArgList()))){
		SourceLocation start_loc_l = l_value_arg->getBeginLoc();
		SourceLocation end_loc_l = GetEndLocOfExpr(l_value_arg, context->comp_inst_);
		if(start_loc_l == start_loc && end_loc_l == end_loc){
			// cout<<"wozhengdemeiyouwenti"<<endl;
			// cout<<"expr: "<<ConvertToString(e, context->comp_inst_->getLangOpts())<<endl;
			return false;
		}
	}

  SourceManager &src_mgr = context->comp_inst_->getSourceManager();
  Rewriter rewriter;
  rewriter.setSourceMgr(src_mgr, context->comp_inst_->getLangOpts());

  string token{ConvertToString(e, context->comp_inst_->getLangOpts())};
  bool is_in_domain = domain_.empty() ? true : 
                      IsStringElementOfSet(token, domain_);

	// VGSR can mutate this expression only if it is a scalar expression
	// inside mutation range and NOT inside array decl size or enum declaration
	return context->IsRangeInMutationRange(SourceRange(start_loc, end_loc)) &&
				 !stmt_context.IsInArrayDeclSize() &&
				 !stmt_context.IsInEnumDecl() &&
         is_in_domain;
}

void VGSR::Mutate(clang::Expr *e, MusicContext *context)
{
	SourceLocation start_loc = e->getBeginLoc();
	SourceLocation end_loc = GetEndLocOfExpr(e, context->comp_inst_);

	string token{ConvertToString(e, context->comp_inst_->getLangOpts())};
	StmtContext &stmt_context = context->getStmtContext();

	// cannot mutate variable in switch condition to a floating-type variable
  bool skip_float_vardecl = stmt_context.IsInSwitchStmtConditionRange(e) ||
                            stmt_context.IsInNonFloatingExprRange(e);

  // cannot mutate a variable in lhs of assignment to a const variable
  bool skip_const_vardecl = stmt_context.IsInLhsOfAssignmentRange(e) ||
                            stmt_context.IsInUnaryIncrementDecrementRange(e);

  bool skip_nonconst_vardecl = stmt_context.IsInSwitchCaseRange(e);

  bool skip_nonconstexpr_float_vardecl = stmt_context.IsInSwitchCaseRange(e);
  vector<string> range;

  for (auto vardecl: *(context->getSymbolTable()->getGlobalScalarVarDeclList()))
  {
    // The rest of loop are VarDecl declared after current point of parsing.
  	if (!(vardecl->getBeginLoc() < start_loc))
  		break;

    string mutated_token{GetVarDeclName(vardecl)};

    // Skip if range is specified and this VarDecl is not in range.
    if (!range_.empty() && !IsStringElementOfSet(mutated_token, range_))
      continue; 

  	if (skip_const_vardecl && IsVarDeclConst(vardecl)) 
      continue;   

    if (skip_nonconst_vardecl && !IsVarDeclConst(vardecl)) 
      continue; 

    if (skip_float_vardecl && IsVarDeclFloating(vardecl))
      continue;

    if (skip_nonconstexpr_float_vardecl && IsVarDeclFloating(vardecl) && !IsVarDeclConstexpr(vardecl))
      continue;

    if (token.compare(mutated_token) != 0)
    {
    	range.push_back(mutated_token);
    }
  }

  // for (auto it: range)
  //   cout << "before range: " << it << endl;

  if (partitions.size() > 0)
    ApplyRangePartition(&range);

  // for (auto it: range)
  //   cout << "after range: " << it << endl;

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

bool VGSR::HandleRangePartition(string option) 
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

void VGSR::ApplyRangePartition(vector<string> *range)
{
  vector<string> range2;
  range2 = *range;

  range->clear();
  sort(range2.begin(), range2.end(), SortStringAscending);

  for (auto part_num: partitions) 
  {
    // Number of possible tokens to mutate to might be smaller than 10.
    // So we do not have 10 partitions.
    if (part_num > range2.size())
    {
      cout << "There are only " << range2.size() << " to mutate to.\n";
      cout << "No partition number " << part_num << endl;
      continue;
    }

    if (range2.size() < num_partitions)
    {
      range->push_back(range2[part_num-1]);
      continue;
    }

    int start_idx = (range2.size() / 10) * (part_num - 1);
    int end_idx = (range2.size() / 10) * part_num;

    if (part_num == 10)
      end_idx = range2.size();

    for (int idx = start_idx; idx < end_idx; idx++)
      range->push_back(range2[idx]);
  }
}
